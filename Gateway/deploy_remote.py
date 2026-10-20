import paramiko
import time
import os
import sys
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
    if not PASSWORD:
        print("[-] Error: SSH password not provided. Set PI_PASSWORD environment variable.")
        sys.exit(1)

    print(f"[*] Connecting to {HOSTNAME} as {USERNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, port=22, username=USERNAME, password=PASSWORD, timeout=10)
        print("[+] Connected successfully.")
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    sftp = ssh.open_sftp()
    remote_dir = f"/home/{USERNAME}"

    for filename, local_path in FILES_TO_UPLOAD.items():
        if os.path.exists(local_path):
            remote_path = f"{remote_dir}/{filename}"
            print(f"[*] Uploading {filename} -> {remote_path}...")
            sftp.put(local_path, remote_path)
            if filename.endswith(".sh"):
                sftp.chmod(remote_path, 0o755)
        else:
            print(f"[!] Warning: Local file missing: {local_path}")

    sftp.close()
    print("[+] All runtime files transferred.")

    print("[*] Reinstalling and starting systemd service...")
    cmd = f"bash {remote_dir}/setup_systemd.sh"
    status, out, err = run_sudo_command(ssh, cmd, PASSWORD)
    print(out)
    if err and "password" not in err.lower():
        print(f"[!] Stderr: {err}")

    print("[*] Verifying gateway service status...")
    status, out, err = run_sudo_command(ssh, "systemctl is-active gateway.service", PASSWORD)
    print(f"[+] Gateway Service Active State: {out.strip()}")

    print("[*] Fetching recent service logs:")
    status, out, err = run_sudo_command(ssh, "journalctl -u gateway.service -n 25 --no-pager", PASSWORD)
    print(out)

    ssh.close()
    print("[SUCCESS] Remote deployment complete.")

if __name__ == "__main__":
    main()
