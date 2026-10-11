import time
import math
import os
import csv
import threading
import subprocess
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import psutil
from scapy.all import AsyncSniffer, TCP, IP
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import pure_rf_multi as active_model

CLASS_LABELS = ["BENIGN", "DDoS", "SSH-Patator"]
LOG_FILE = "stress_test_log.csv"
LOG_INTERVAL_SECONDS = 300

try:
    pi_ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip().split()[0]
except Exception:
    pi_ip = "127.0.0.1"

WHITELIST_IPS = {"192.168.137.1", "192.168.10.1", "127.0.0.1", pi_ip}
blocked_ips = set()
active_flows = {}

stats = {
    "packets_sniffed": 0,
    "benign_flows": 0,
    "anomalous_flows": 0,
    "start_time": time.time(),
    "recent_logs": [],
    "blocked_list": [],
    "latencies": []
}

def init_csv_logger():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "uptime_seconds", "cpu_percent", "ram_percent",
                "packets_sniffed", "benign_flows", "anomalous_flows",
                "active_flows_in_ram", "avg_latency_ms"
            ])

def stress_test_logger_daemon():
    init_csv_logger()
    while True:
        try:
            time.sleep(LOG_INTERVAL_SECONDS)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uptime = int(time.time() - stats["start_time"])
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            
            recent_latencies = stats["latencies"][-50:] if stats["latencies"] else [0.08]
            avg_lat = sum(recent_latencies) / len(recent_latencies) if recent_latencies else 0.08

            with open(LOG_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    now_str,
                    uptime,
                    cpu,
                    ram,
                    stats["packets_sniffed"],
                    stats["benign_flows"],
                    stats["anomalous_flows"],
                    len(active_flows),
                    f"{avg_lat:.4f}"
                ])
        except Exception:
            pass

logger_thread = threading.Thread(target=stress_test_logger_daemon, daemon=True)
logger_thread.start()

def extract_features(packet):
    stats["packets_sniffed"] += 1

    if IP not in packet or TCP not in packet:
        return

    src_ip, dst_ip = packet[IP].src, packet[IP].dst
    if src_ip in blocked_ips:
        return

    sport, dport = packet[TCP].sport, packet[TCP].dport
    flow_key = tuple(sorted([f"{src_ip}:{sport}", f"{dst_ip}:{dport}"]))
    current_time = time.time()
    packet_length = len(packet)

    if flow_key not in active_flows:
        active_flows[flow_key] = {
            'first_src': src_ip,
            'first_sport': sport,
            'start_time': current_time,
            'last_time': current_time,
            'fwd_packets': 0,
            'bwd_packets': 0,
            'fwd_length_sum': 0,
            'syn_count': 0,
            'bwd_lengths': [],
            'iat_sum': 0,
            'iat_count': 0,
            'init_win_bytes_fwd': packet[TCP].window,
            'destination_port': dport
        }

    flow = active_flows[flow_key]
    direction = "fwd" if (src_ip == flow['first_src'] and sport == flow['first_sport']) else "bwd"

    iat = current_time - flow['last_time']
    if flow['fwd_packets'] + flow['bwd_packets'] > 0:
        flow['iat_sum'] += iat
        flow['iat_count'] += 1
    flow['last_time'] = current_time

    if packet[TCP].flags & 0x02:
        flow['syn_count'] += 1

    if direction == "fwd":
        flow['fwd_packets'] += 1
        flow['fwd_length_sum'] += packet_length
    else:
        flow['bwd_packets'] += 1
        flow['bwd_lengths'].append(packet_length)

    total_pkts = flow['fwd_packets'] + flow['bwd_packets']

    if total_pkts % 5 == 0:
        flow_duration = (current_time - flow['start_time']) * 1000000
        iat_mean = (flow['iat_sum'] / flow['iat_count']) * 1000000 if flow['iat_count'] > 0 else 0
        fwd_len_mean = flow['fwd_length_sum'] / flow['fwd_packets'] if flow['fwd_packets'] > 0 else 0

        if len(flow['bwd_lengths']) > 1:
            mean = sum(flow['bwd_lengths']) / len(flow['bwd_lengths'])
            bwd_len_std = math.sqrt(sum([((x - mean) ** 2) for x in flow['bwd_lengths']]) / len(flow['bwd_lengths']))
        else:
            bwd_len_std = 0.0

        feature_row = [
            flow['destination_port'],
            bwd_len_std,
            flow['syn_count'],
            iat_mean,
            flow['fwd_packets'],
            flow_duration,
            fwd_len_mean,
            flow['init_win_bytes_fwd']
        ]

        inf_start = time.perf_counter()
        scores = active_model.score(feature_row)
        class_idx = scores.index(max(scores))
        prediction = CLASS_LABELS[class_idx]
        latency = (time.perf_counter() - inf_start) * 1000
        stats["latencies"].append(latency)
        if len(stats["latencies"]) > 200:
            stats["latencies"] = stats["latencies"][-200:]

        explanation = "Normal Traffic"
        if prediction == "SSH-Patator":
            explanation = "Brute-Force Pattern"
        elif prediction == "DDoS":
            explanation = "Flood Traffic"

        if iat_mean < 1000 or flow['syn_count'] > 15:
            prediction = "DDoS (Volumetric)"
            explanation = f"High Packet Rate (SYNs: {flow['syn_count']}, IAT: {iat_mean:.0f}us)"

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if prediction == "BENIGN":
            stats["benign_flows"] += 1
            stats["recent_logs"].insert(0, (timestamp, str(flow['destination_port']), "BENIGN", f"{latency:.2f}ms"))
        else:
            stats["anomalous_flows"] += 1
            stats["recent_logs"].insert(0, (timestamp, str(flow['destination_port']), str(prediction), f"{latency:.2f}ms"))

            if src_ip not in WHITELIST_IPS and src_ip not in blocked_ips:
                try:
                    subprocess.run(["iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"], check=False)
                    subprocess.run(["iptables", "-A", "FORWARD", "-s", src_ip, "-j", "DROP"], check=False)
                except Exception:
                    pass
                blocked_ips.add(src_ip)
                stats["blocked_list"].insert(0, (src_ip, str(prediction), explanation))

        stats["recent_logs"] = stats["recent_logs"][:15]

def generate_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3)
    )
    layout["left"].split_column(
        Layout(name="traffic", size=6),
        Layout(name="logs", ratio=2)
    )

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    uptime = int(time.time() - stats["start_time"])
    recent_lats = stats["latencies"][-50:] if stats["latencies"] else [0.08]
    cur_lat = sum(recent_lats) / len(recent_lats) if recent_lats else 0.08

    header_text = (
        f"AUTONOMOUS EDGE-AI GATEWAY | CPU: {cpu}% | RAM: {ram}% | Uptime: {uptime}s\n"
        f"[bold yellow]Model: Multi-Dataset (2017+2018+2019) | Accuracy: 96.70% | Latency: {cur_lat:.2f}ms | Log: {LOG_FILE}[/bold yellow]"
    )
    layout["header"].update(Panel(Text.from_markup(header_text, justify="center"), style="green"))

    traffic_txt = (
        f"Packets Sniffed : [bold white]{stats['packets_sniffed']}[/]\n"
        f"Active Flows RAM: [bold white]{len(active_flows)}[/]\n"
        f"Benign Flows    : [bold green]{stats['benign_flows']}[/]\n"
        f"Blocked Threats : [bold red]{stats['anomalous_flows']}[/]"
    )
    layout["traffic"].update(Panel(traffic_txt, title="[1] LIVE TRAFFIC INGESTION", border_style="cyan"))

    log_table = Table(expand=True)
    log_table.add_column("Time", style="dim")
    log_table.add_column("Port")
    log_table.add_column("Classification")
    log_table.add_column("Latency")
    for log in stats["recent_logs"]:
        color = "green" if log[2] == "BENIGN" else "red bold"
        log_table.add_row(log[0], log[1], f"[{color}]{log[2]}[/{color}]", log[3])
    layout["logs"].update(Panel(log_table, title="[2] INFERENCE LOG", border_style="cyan"))

    mit_table = Table(expand=True)
    mit_table.add_column("Attacker IP", style="red bold", width=15)
    mit_table.add_column("Threat", style="red", width=16)
    mit_table.add_column("Reason", style="yellow")
    for ip, threat, explanation in stats["blocked_list"]:
        mit_table.add_row(f"[red]{ip}[/red]", threat, explanation)
    layout["right"].update(Panel(mit_table, title="[3] MITIGATION ACTION", border_style="red bold"))

    return layout

if __name__ == "__main__":
    sniffer = AsyncSniffer(iface="eth0", prn=extract_features, store=False)
    sniffer.start()

    with Live(generate_dashboard(), refresh_per_second=4) as live:
        try:
            while True:
                time.sleep(0.25)
                live.update(generate_dashboard())
        except KeyboardInterrupt:
            sniffer.stop()
