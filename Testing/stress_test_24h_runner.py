import time
import os
import sys
import csv
import socket
import json
import random
import ctypes
from datetime import datetime
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HOSTNAME = os.getenv("PI_IP", "192.168.137.2")
USERNAME = os.getenv("PI_USER", "fyp1512")
PASSWORD = os.getenv("PI_PASSWORD", "FYP@1512")

TOTAL_HOURS = 24
CHECKPOINT_INTERVAL_SEC = 300
TOTAL_CHECKPOINTS = int((TOTAL_HOURS * 3600) / CHECKPOINT_INTERVAL_SEC)
ATTACK_PULSE_EVERY_N_CHECKPOINTS = 12

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "history_24h_stress_log.csv")

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_AWAYMODE_REQUIRED = 0x00000040

def set_windows_keep_awake():
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
        )
        return True
    except Exception:
        return False

def reset_windows_sleep():
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except Exception:
        pass

def init_csv():
    file_exists = os.path.exists(LOG_FILE)
    if not file_exists:
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "checkpoint", "timestamp", "elapsed_seconds", "traffic_phase",
                "pi_cpu_percent", "pi_ram_rss_mb", "pi_system_ram_percent",
                "pi_temp_c", "active_iptables_rules", "syn_ttb_ms",
                "ssh_ttb_ms", "benign_flows_sent", "benign_drops",
                "attacks_mitigated"
            ])

def append_csv_row(row):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
        f.flush()
        os.fsync(f.fileno())

def query_pi_telemetry():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=5)

        cmd = (
            "python3 -c \""
            "import psutil, subprocess, json\n"
            "temp = 0.0\n"
            "try:\n"
            "    with open('/sys/class/thermal/thermal_zone0/temp') as f:\n"
            "        temp = float(f.read().strip()) / 1000.0\n"
            "except Exception:\n"
            "    pass\n"
            "daemon_rss = 0.0\n"
            "for p in psutil.process_iter(['name', 'cmdline', 'memory_info']):\n"
            "    try:\n"
            "        cmdline = ' '.join(p.info['cmdline'] or [])\n"
            "        if 'dashboard.py' in cmdline:\n"
            "            daemon_rss = p.info['memory_info'].rss / (1024*1024)\n"
            "            break\n"
            "    except Exception:\n"
            "        pass\n"
            "rules = 0\n"
            "try:\n"
            "    out = subprocess.check_output(['sudo', 'iptables', '-L', 'INPUT', '-n']).decode('utf-8')\n"
            "    rules = max(0, len([l for l in out.splitlines() if l.strip()]) - 2)\n"
            "except Exception:\n"
            "    pass\n"
            "print(json.dumps({'cpu': psutil.cpu_percent(), 'ram': psutil.virtual_memory().percent, 'rss_mb': round(daemon_rss, 2), 'temp_c': round(temp, 1), 'rules': rules}))\""
        )

        stdin, stdout, stderr = ssh.exec_command(cmd)
        res = stdout.read().decode('utf-8').strip()
        ssh.close()
        return json.loads(res)
    except Exception as e:
        return {'cpu': 0.0, 'ram': 0.0, 'rss_mb': 0.0, 'temp_c': 0.0, 'rules': 0, 'error': str(e)}

def dispatch_ambient_benign_traffic(duration_sec=280):
    start_t = time.time()
    flows_sent = 0
    drops = 0
    while time.time() - start_t < duration_sec:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            port = 80 if random.random() > 0.3 else 22
            res = s.connect_ex((HOSTNAME, port))
            if res != 0 and res != 10035 and res != 10061:
                drops += 1
            else:
                flows_sent += 1
            s.close()
        except Exception:
            drops += 1
        time.sleep(random.uniform(3.0, 7.0))
    return flows_sent, drops

def execute_remote_attack_pulse():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)

    pulse_code = """
import time
import json
import random
import subprocess
from scapy.all import sendp, Ether, IP, TCP

def get_br0_mac():
    try:
        out = subprocess.check_output(['cat', '/sys/class/net/br0/address']).decode('utf-8').strip()
        return out
    except Exception:
        return '88:a2:9e:a7:14:28'

br0_mac = get_br0_mac()

def check_blocked(ip):
    try:
        out = subprocess.check_output(['iptables', '-L', 'INPUT', '-n']).decode('utf-8')
        return ip in out
    except Exception:
        return False

target_ip = "192.168.137.2"
res = {}

# 1. Volumetric SYN Flood Pulse
syn_ip = f"192.168.137.{random.randint(150, 199)}"
syn_pkts = [
    Ether(dst=br0_mac)/IP(src=syn_ip, dst=target_ip)/TCP(sport=10000+i, dport=80, flags="S", window=1024)
    for i in range(35)
]

t0 = time.perf_counter()
sendp(syn_pkts, iface="br0", verbose=False)
syn_blocked = False
syn_ttb = 0.0

for _ in range(50):
    if check_blocked(syn_ip):
        syn_ttb = (time.perf_counter() - t0) * 1000.0
        syn_blocked = True
        break
    time.sleep(0.01)

res['syn_blocked'] = syn_blocked
res['syn_ttb_ms'] = round(syn_ttb, 2)

# 2. SSH Brute-Force Pulse
ssh_ip = f"192.168.137.{random.randint(202, 250)}"
ssh_pkts = [
    Ether(dst=br0_mac)/IP(src=ssh_ip, dst=target_ip)/TCP(sport=20000+(i%5), dport=22, flags="S", window=65535)
    for i in range(25)
]

t0_ssh = time.perf_counter()
sendp(ssh_pkts, iface="br0", verbose=False)
ssh_blocked = False
ssh_ttb = 0.0

for _ in range(50):
    if check_blocked(ssh_ip):
        ssh_ttb = (time.perf_counter() - t0_ssh) * 1000.0
        ssh_blocked = True
        break
    time.sleep(0.01)

res['ssh_blocked'] = ssh_blocked
res['ssh_ttb_ms'] = round(ssh_ttb, 2)

# Clean test rules
subprocess.run(['iptables', '-D', 'INPUT', '-s', syn_ip, '-j', 'DROP'], stderr=subprocess.DEVNULL)
subprocess.run(['iptables', '-D', 'FORWARD', '-s', syn_ip, '-j', 'DROP'], stderr=subprocess.DEVNULL)
subprocess.run(['iptables', '-D', 'INPUT', '-s', ssh_ip, '-j', 'DROP'], stderr=subprocess.DEVNULL)
subprocess.run(['iptables', '-D', 'FORWARD', '-s', ssh_ip, '-j', 'DROP'], stderr=subprocess.DEVNULL)

print("PULSE_OUT:" + json.dumps(res))
"""
    sftp = ssh.open_sftp()
    with sftp.file("/home/fyp1512/pulse_exec.py", "w") as f:
        f.write(pulse_code)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command("sudo python3 /home/fyp1512/pulse_exec.py")
    raw_out = stdout.read().decode('utf-8', errors='replace')
    ssh.close()

    for line in raw_out.splitlines():
        if line.startswith("PULSE_OUT:"):
            return json.loads(line[len("PULSE_OUT:"):])
    return {'syn_blocked': False, 'syn_ttb_ms': 0.0, 'ssh_blocked': False, 'ssh_ttb_ms': 0.0}

def main():
    print("==================================================================")
    print(" 24-HOUR DIURNAL RELIABILITY & STRESS SOAK TEST HARNESS")
    print(f" Target Edge Gateway: {HOSTNAME} | Total Target: {TOTAL_HOURS} Hours")
    print(f" Checkpoint Interval : {CHECKPOINT_INTERVAL_SEC}s (Every 5 minutes)")
    print(f" Log File            : {LOG_FILE}")
    print("==================================================================")

    init_csv()
    keep_awake = set_windows_keep_awake()
    if keep_awake:
        print("[+] Windows sleep inhibition active: Laptop will stay awake.")
    else:
        print("[!] Note: SetThreadExecutionState not available; ensure power settings prevent sleep.")

    start_time = time.time()
    total_attacks_mitigated = 0
    total_benign_sent = 0
    total_benign_drops = 0
    last_syn_ttb = 0.0
    last_ssh_ttb = 0.0

    print(f"[*] Starting 24-hour execution cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    print("    Press Ctrl+C at any time to pause or generate interim reports.")

    try:
        for cp in range(1, TOTAL_CHECKPOINTS + 1):
            cp_start = time.time()
            elapsed_total = int(cp_start - start_time)
            is_attack_pulse = (cp % ATTACK_PULSE_EVERY_N_CHECKPOINTS == 0) or (cp == 1)

            if is_attack_pulse:
                phase_name = "ATTACK_PULSE"
                print(f"\n[!] Checkpoint {cp}/{TOTAL_CHECKPOINTS} | Hour {cp/12:.1f}: Dispatching Hourly Attack Pulse...")
                attack_res = execute_remote_attack_pulse()
                last_syn_ttb = attack_res.get('syn_ttb_ms', 0.0)
                last_ssh_ttb = attack_res.get('ssh_ttb_ms', 0.0)
                if attack_res.get('syn_blocked'):
                    total_attacks_mitigated += 1
                if attack_res.get('ssh_blocked'):
                    total_attacks_mitigated += 1
                print(f"    -> SYN Flood TTB : {last_syn_ttb} ms (Mitigated: {attack_res.get('syn_blocked')})")
                print(f"    -> SSH Brute TTB : {last_ssh_ttb} ms (Mitigated: {attack_res.get('ssh_blocked')})")
                benign_sent, benign_drops = dispatch_ambient_benign_traffic(duration_sec=270)
            else:
                phase_name = "AMBIENT_BENIGN"
                benign_sent, benign_drops = dispatch_ambient_benign_traffic(duration_sec=285)

            total_benign_sent += benign_sent
            total_benign_drops += benign_drops

            telem = query_pi_telemetry()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            row = [
                cp, now_str, elapsed_total, phase_name,
                telem['cpu'], telem['rss_mb'], telem['ram'],
                telem['temp_c'], telem['rules'], last_syn_ttb,
                last_ssh_ttb, total_benign_sent, total_benign_drops,
                total_attacks_mitigated
            ]
            append_csv_row(row)

            rem_hours = ((TOTAL_CHECKPOINTS - cp) * CHECKPOINT_INTERVAL_SEC) / 3600.0
            print(f"[*] CP {cp:03d}/{TOTAL_CHECKPOINTS} [{now_str}] | CPU: {telem['cpu']}% | RSS: {telem['rss_mb']}MB | RAM: {telem['ram']}% | Temp: {telem['temp_c']}C | Rules: {telem['rules']} | Rem: {rem_hours:.1f}h")

            cp_elapsed = time.time() - cp_start
            sleep_remaining = max(0.0, CHECKPOINT_INTERVAL_SEC - cp_elapsed)
            if sleep_remaining > 0:
                time.sleep(sleep_remaining)

    except KeyboardInterrupt:
        print("\n\n[!] User interrupted test execution (Ctrl+C).")
    finally:
        reset_windows_sleep()
        total_run_sec = int(time.time() - start_time)
        print("==================================================================")
        print(f" Test session ended. Total active run: {total_run_sec/3600.0:.2f} hours ({total_run_sec} seconds).")
        print(f" All checkpoints saved to: {LOG_FILE}")
        print(" To generate visual graphs, run: python Testing/plot_24h_stress.py")
        print("==================================================================")

if __name__ == "__main__":
    main()
