import paramiko
import time
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HOSTNAME = "192.168.137.2"
USERNAME = "fyp1512"
PASSWORD = "FYP@1512"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

FILES_TO_UPLOAD = {
    "dashboard.py": os.path.join(SCRIPT_DIR, "dashboard.py"),
    "pure_rf_multi.py": os.path.join(SCRIPT_DIR, "pure_rf_multi.py"),
    "gateway.service": os.path.join(SCRIPT_DIR, "gateway.service"),
    "setup_systemd.sh": os.path.join(SCRIPT_DIR, "setup_systemd.sh"),
    "plot_stress_test.py": os.path.join(PROJECT_ROOT, "Testing", "plot_stress_test.py"),
    "simulate_traffic.py": os.path.join(PROJECT_ROOT, "Testing", "simulate_traffic.py")
}

def run_sudo_command(ssh, command, password):
    stdin, stdout, stderr = ssh.exec_command(f"sudo -S -p '' {command}")
    stdin.write(password + "\n")
    stdin.flush()
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return exit_status, out, err

def main():
    print(f"[*] Connecting to {HOSTNAME} as {USERNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, port=22, username=USERNAME, password=PASSWORD, timeout=10)
        print("[+] SSH connection successful!")
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return 1

    stdin, stdout, stderr = ssh.exec_command("hostname && uname -a && uptime")
    sys_info = stdout.read().decode('utf-8').strip()
    print(f"[+] Remote host information:\n{sys_info}\n")

    print("[*] Transferring files via SFTP...")
    sftp = ssh.open_sftp()
    for remote_name, local_path in FILES_TO_UPLOAD.items():
        if os.path.exists(local_path):
            remote_path = f"/home/{USERNAME}/{remote_name}"
            print(f"  -> Uploading {remote_name} to {remote_path}...")
            sftp.put(local_path, remote_path)
        else:
            print(f"  [!] Local file {local_path} not found!")
    sftp.close()
    print("[+] All files transferred.\n")

    run_sudo_command(ssh, f"chmod +x /home/{USERNAME}/setup_systemd.sh", PASSWORD)

    print("[*] Installing gateway.service via systemd...")
    code, out, err = run_sudo_command(ssh, f"bash /home/{USERNAME}/setup_systemd.sh", PASSWORD)
    print(f"[+] Script output:\n{out}")
    if err:
        print(f"[!] Stderr:\n{err}")

    time.sleep(3)
    print("\n[*] Checking service status...")
    code, out, err = run_sudo_command(ssh, "systemctl status gateway.service --no-pager", PASSWORD)
    print(out)

    print("\n[*] Reading recent service logs...")
    code, out, err = run_sudo_command(ssh, "journalctl -u gateway.service -n 25 --no-pager", PASSWORD)
    print(out)

    ssh.close()
    print("\n[SUCCESS] Deployment complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
