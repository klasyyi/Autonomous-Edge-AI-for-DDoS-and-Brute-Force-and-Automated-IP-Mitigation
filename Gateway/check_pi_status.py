import os
import sys
import paramiko
import getpass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HOSTNAME = os.getenv("PI_IP", "192.168.137.2")
USERNAME = os.getenv("PI_USER", "fyp1512")
PASSWORD = os.getenv("PI_PASSWORD")

if not PASSWORD:
    if sys.stdin.isatty():
        PASSWORD = getpass.getpass(f"Enter SSH password for {USERNAME}@{HOSTNAME}: ")
    else:
        PASSWORD = os.getenv("PI_PASSWORD", "")

def run_sudo(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' {cmd}")
    stdin.write(PASSWORD + "\n")
    stdin.flush()
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8', errors='replace').strip()

def main():
    if not PASSWORD:
        print("[-] Error: SSH password not provided. Set PI_PASSWORD environment variable.")
        sys.exit(1)

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
