import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "history", "history_24h_stress_log.csv")

def plot_24h_telemetry(df):
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(11, 7.5), dpi=300, sharex=True)

    color_cpu = '#d9534f'
    color_temp = '#f0ad4e'
    ax_top.set_ylabel('CPU Utilization (%)', color=color_cpu, fontsize=11, fontweight='bold')
    ax_top.plot(df['timestamp'], df['pi_cpu_percent'], color=color_cpu, linewidth=1.8, marker='o', markersize=3, label='CPU (%)')
    ax_top.tick_params(axis='y', labelcolor=color_cpu)
    ax_top.set_ylim(0, 100)

    ax_temp = ax_top.twinx()
    ax_temp.set_ylabel('SoC Temperature (C)', color='#c97a00', fontsize=11, fontweight='bold')
    ax_temp.plot(df['timestamp'], df['pi_temp_c'], color=color_temp, linewidth=1.8, linestyle='-.', marker='^', markersize=3, label='SoC Temp (C)')
    ax_temp.axhline(y=80.0, color='r', linestyle=':', linewidth=1.2, label='Thermal Throttle Limit (80 C)')
    ax_temp.tick_params(axis='y', labelcolor='#c97a00')
    ax_temp.set_ylim(20, 90)

    lines_top, labels_top = ax_top.get_legend_handles_labels()
    lines_temp, labels_temp = ax_temp.get_legend_handles_labels()
    ax_top.legend(lines_top + lines_temp, labels_top + labels_temp, loc='upper left', frameon=True)
    ax_top.set_title('Edge Appliance 24-Hour Soak Test: Compute Utilization & Thermal Stability Profile', fontsize=12, fontweight='bold', pad=12)

    color_rss = '#0275d8'
    color_sys_ram = '#5bc0de'
    ax_bot.set_ylabel('Daemon RSS (MB)', color=color_rss, fontsize=11, fontweight='bold')
    ax_bot.plot(df['timestamp'], df['pi_ram_rss_mb'], color=color_rss, linewidth=1.8, marker='s', markersize=3, label='Daemon RSS (MB)')
    ax_bot.tick_params(axis='y', labelcolor=color_rss)
    ax_bot.set_ylim(0, max(50.0, df['pi_ram_rss_mb'].max() * 1.5))

    ax_sys_ram = ax_bot.twinx()
    ax_sys_ram.set_ylabel('System RAM Utilization (%)', color='#17a2b8', fontsize=11, fontweight='bold')
    ax_sys_ram.plot(df['timestamp'], df['pi_system_ram_percent'], color=color_sys_ram, linewidth=1.6, linestyle='--', label='System RAM (%)')
    ax_sys_ram.tick_params(axis='y', labelcolor='#17a2b8')
    ax_sys_ram.set_ylim(0, 100)

    lines_bot, labels_bot = ax_bot.get_legend_handles_labels()
    lines_ram, labels_ram = ax_sys_ram.get_legend_handles_labels()
    ax_bot.legend(lines_bot + lines_ram, labels_bot + labels_ram, loc='upper left', frameon=True)
    ax_bot.set_title('Memory Footprint Stability (Demonstrating Zero Leakage Across Diurnal Duty Cycle)', fontsize=11, fontweight='bold', pad=10)
    ax_bot.set_xlabel('Timestamp', fontsize=11, fontweight='bold', labelpad=8)
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.tight_layout()
    out_path = os.path.join(SCRIPT_DIR, "stress_test_24h_telemetry.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved hardware telemetry chart to: {out_path}")

def plot_24h_mitigation(df):
    fig, (ax_ttb, ax_cum) = plt.subplots(2, 1, figsize=(11, 7.5), dpi=300, sharex=True)

    pulse_df = df[df['traffic_phase'] == 'ATTACK_PULSE']
    if len(pulse_df) > 0:
        ax_ttb.plot(pulse_df['timestamp'], pulse_df['syn_ttb_ms'], color='#d9534f', marker='o', markersize=5, linewidth=1.8, label='SYN Flood Time-to-Block (ms)')
        ax_ttb.plot(pulse_df['timestamp'], pulse_df['ssh_ttb_ms'], color='#6f42c1', marker='^', markersize=5, linewidth=1.8, linestyle='--', label='SSH Brute Time-to-Block (ms)')
        ax_ttb.axhline(y=100.0, color='black', linestyle=':', linewidth=1.2, label='100 ms Real-Time Mitigation Boundary')
    ax_ttb.set_ylabel('Mitigation Latency (ms)', fontsize=11, fontweight='bold')
    ax_ttb.set_ylim(0, max(150.0, (df['syn_ttb_ms'].max() if len(df) > 0 else 100) * 1.3))
    ax_ttb.legend(loc='upper right', frameon=True)
    ax_ttb.set_title('Physical Inline Closed-Loop Attack Mitigation Latency Across 24 Hours', fontsize=12, fontweight='bold', pad=12)

    ax_cum.plot(df['timestamp'], df['benign_flows_sent'], color='#5cb85c', linewidth=1.8, label='Benign Ingress Sessions')
    ax_cum.plot(df['timestamp'], df['attacks_mitigated'], color='#d9534f', linewidth=1.8, marker='x', markersize=4, label='Attacks Successfully Blocked')
    ax_cum.plot(df['timestamp'], df['benign_drops'], color='#000000', linewidth=1.2, linestyle=':', label='Benign Traffic Drops (0 = 0% FPR)')
    ax_cum.set_ylabel('Cumulative Flow Events', fontsize=11, fontweight='bold')
    ax_cum.set_xlabel('Timestamp', fontsize=11, fontweight='bold', labelpad=8)
    max_flow = max(10.0, float(df['benign_flows_sent'].max() if len(df) > 0 else 10.0))
    ax_cum.set_ylim(-0.5, max_flow * 1.15)
    ax_cum.legend(loc='upper left', frameon=True)
    ax_cum.set_title('Ingress Traffic Distribution and False Positive Rate Reliability', fontsize=11, fontweight='bold', pad=10)
    ax_cum.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.tight_layout()
    out_path = os.path.join(SCRIPT_DIR, "stress_test_24h_mitigation.png")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved mitigation performance chart to: {out_path}")

def main():
    if not os.path.exists(LOG_FILE):
        print(f"[-] Log file not found at: {LOG_FILE}")
        return

    df = pd.read_csv(LOG_FILE)
    if len(df) == 0:
        print("[-] Log file is empty.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"[*] Processing {len(df)} checkpoints from {LOG_FILE}...")
    plot_24h_telemetry(df)
    plot_24h_mitigation(df)

if __name__ == "__main__":
    main()
