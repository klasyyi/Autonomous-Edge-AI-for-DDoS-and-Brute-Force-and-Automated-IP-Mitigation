import time
import socket
import sys
import argparse
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GATEWAY_IP = "192.168.137.2"

def send_benign_traffic(target_ip, port=80, count=20, delay=0.2):
    print(f"[*] Sending benign HTTP traffic to {target_ip}:{port} ({count} flows)")
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect_ex((target_ip, port))
            s.close()
            time.sleep(delay)
            if (i + 1) % 5 == 0:
                print(f"  [+] Sent {i + 1}/{count} flows")
        except Exception:
            pass
    print("[SUCCESS] Benign traffic simulation complete.")

def send_ssh_bruteforce_simulation(target_ip, port=22, count=30, delay=0.05):
    print(f"[*] Sending SSH brute-force attempts to {target_ip}:{port} ({count} attempts)")
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect_ex((target_ip, port))
            s.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n")
            s.close()
            time.sleep(delay)
            if (i + 1) % 5 == 0:
                print(f"  [!] Sent {i + 1}/{count} brute-force probes")
        except Exception:
            pass
    print("[SUCCESS] SSH brute-force simulation complete.")

def send_syn_flood_simulation(target_ip, port=80, burst=100):
    print(f"[*] Sending SYN flood packets to {target_ip}:{port} ({burst} packets)")
    for i in range(burst):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(False)
            s.connect_ex((target_ip, port))
            s.close()
            time.sleep(0.001)
        except Exception:
            pass
    print("[SUCCESS] SYN flood simulation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FYP Edge Gateway Traffic Generator")
    parser.add_argument("--target", default=GATEWAY_IP, help="Target Gateway IP")
    parser.add_argument("--mode", choices=["benign", "ssh", "ddos", "all"], default="all", help="Traffic mode")

    args = parser.parse_args()

    print(f"==================================================")
    print(f" Edge-AI Traffic Generator")
    print(f" Target: {args.target} | Time: {datetime.now()}")
    print(f"==================================================")

    if args.mode in ["benign", "all"]:
        send_benign_traffic(args.target)
        time.sleep(2)

    if args.mode in ["ssh", "all"]:
        send_ssh_bruteforce_simulation(args.target)
        time.sleep(2)

    if args.mode in ["ddos", "all"]:
        send_syn_flood_simulation(args.target)

    print("==================================================")
    print(" Simulation complete.")
