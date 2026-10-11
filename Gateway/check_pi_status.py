import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HOSTNAME = "192.168.137.2"
USERNAME = "fyp1512"
PASSWORD = "FYP@1512"

def run_sudo(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' {cmd}")
    stdin.write(PASSWORD + "\n")
    stdin.flush()
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8', errors='replace').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, port=22, username=USERNAME, password=PASSWORD, timeout=10)

    print("==================================================")
    print(" RASPBERRY PI GATEWAY LIVE TELEMETRY REPORT")
    print("==================================================")

    svc = run_sudo(ssh, "systemctl is-active gateway.service")
    print(f"[*] Gateway Service Active State: {svc}")

    uptime = run_sudo(ssh, "uptime")
    print(f"[*] System Uptime & Load: {uptime}")

    mem = run_sudo(ssh, "free -h")
    print(f"[*] Memory Utilization:\n{mem}\n")

    print("[*] Inspecting /home/fyp1512/stress_test_log.csv:")
    csv_content = run_sudo(ssh, "cat /home/fyp1512/stress_test_log.csv 2>/dev/null || echo 'Log file initializing...'")
    print(csv_content)

    print("\n[*] Active Linux iptables Rules:")
    ipt = run_sudo(ssh, "iptables -L INPUT -v -n --line-numbers")
    print(ipt)

    ssh.close()
    print("==================================================")

if __name__ == "__main__":
    main()
