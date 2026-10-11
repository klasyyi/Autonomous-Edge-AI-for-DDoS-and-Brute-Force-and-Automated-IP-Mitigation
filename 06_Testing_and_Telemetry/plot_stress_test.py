import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "stress_test_log.csv")

def generate_stress_test_charts(csv_file=CSV_PATH):
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} does not exist.")
        return

    df = pd.read_csv(csv_file)
    if len(df) < 2:
        print("Need at least 2 log entries to plot trends. Collected:", len(df))
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig, ax1 = plt.subplots(figsize=(10, 4.5), dpi=300)

    color_cpu = '#d9534f'
    ax1.set_xlabel('Timestamp', fontsize=11, fontweight='bold', labelpad=10)
    ax1.set_ylabel('CPU Utilization (%)', color=color_cpu, fontsize=11, fontweight='bold')
    ax1.plot(df['timestamp'], df['cpu_percent'], color=color_cpu, linewidth=1.8, marker='o', markersize=3, label='CPU (%)')
    ax1.tick_params(axis='y', labelcolor=color_cpu)
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    color_ram = '#0275d8'
    ax2.set_ylabel('RAM Utilization (%)', color=color_ram, fontsize=11, fontweight='bold')
    ax2.plot(df['timestamp'], df['ram_percent'], color=color_ram, linewidth=1.8, linestyle='--', marker='s', markersize=3, label='RAM (%)')
    ax2.tick_params(axis='y', labelcolor=color_ram)
    ax2.set_ylim(0, 100)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.title('Raspberry Pi 4 Resource Utilization Over Time', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    output_fig1 = os.path.join(SCRIPT_DIR, "stress_test_cpu_ram.png")
    plt.savefig(output_fig1, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved hardware chart to: {output_fig1}")

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 6), dpi=300, sharex=True)

    ax_top.plot(df['timestamp'], df['benign_flows'], label='Benign Flows', color='#5cb85c', linewidth=1.6)
    ax_top.plot(df['timestamp'], df['anomalous_flows'], label='Blocked Threats', color='#d9534f', linewidth=1.6)
    ax_top.set_ylabel('Cumulative Flows', fontsize=10, fontweight='bold')
    ax_top.legend(loc='upper left', frameon=True)
    ax_top.set_title('Cumulative Network Flows and Threat Mitigation', fontsize=11, fontweight='bold')

    ax_bot.plot(df['timestamp'], df['avg_latency_ms'], label='Inference Latency (ms)', color='#6f42c1', linewidth=1.6, marker='^', markersize=4)
    ax_bot.axhline(y=0.10, color='r', linestyle=':', label='Target Threshold (0.10ms)')
    ax_bot.set_ylabel('Latency (ms)', fontsize=10, fontweight='bold')
    ax_bot.set_xlabel('Timestamp', fontsize=10, fontweight='bold', labelpad=8)
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax_bot.legend(loc='upper right', frameon=True)
    fig.autofmt_xdate()

    plt.tight_layout()
    output_fig2 = os.path.join(SCRIPT_DIR, "stress_test_latency_flows.png")
    plt.savefig(output_fig2, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved flow & latency chart to: {output_fig2}")

if __name__ == "__main__":
    generate_stress_test_charts()
