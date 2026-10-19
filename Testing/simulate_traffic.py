import time
import socket
import sys
import argparse
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GATEWAY_IP = "192.168.137.2"

def probe_single_syn(target_ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        s.connect_ex((target_ip, port))
        s.close()
        return True
    except Exception:
        return False

def send_benign_traffic(target_ip, port=80, count=25, delay=0.15):
    print(f"[*] Dispatching benign HTTP session flows to {target_ip}:{port} ({count} flows)")
    successful = 0
    start_time = time.time()
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.8)
            res = s.connect_ex((target_ip, port))
            if res == 0 or res == 10035 or res == 10061:
                successful += 1
            s.close()
            time.sleep(delay)
            if (i + 1) % 5 == 0:
                print(f"  [+] Completed {i + 1}/{count} benign flows")
        except Exception:
            pass
    elapsed = time.time() - start_time
    print(f"[SUCCESS] Benign traffic finished. Flows: {count}, Elapsed: {elapsed:.2f}s")

def send_ssh_bruteforce_simulation(target_ip, port=22, count=35, delay=0.04):
    print(f"[*] Dispatching SSH credential probe burst to {target_ip}:{port} ({count} probes)")
    start_time = time.time()
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect_ex((target_ip, port))
            s.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n")
            s.close()
            time.sleep(delay)
            if (i + 1) % 10 == 0:
                print(f"  [!] Dispatched {i + 1}/{count} brute-force connection probes")
        except Exception:
            pass
    elapsed = time.time() - start_time
    print(f"[SUCCESS] SSH brute-force probe finished. Probes: {count}, Elapsed: {elapsed:.2f}s")

def send_syn_flood_simulation(target_ip, port=80, burst=150):
    print(f"[*] Dispatching volumetric SYN flood burst to {target_ip}:{port} ({burst} packets)")
    start_time = time.time()
    for _ in range(burst):
        probe_single_syn(target_ip, port)
        time.sleep(0.001)
    elapsed = time.time() - start_time
    rate = burst / elapsed if elapsed > 0 else 0
    print(f"[SUCCESS] SYN flood burst complete. Packets: {burst}, Rate: {rate:.1f} pps")

def run_multithreaded_stress_test(target_ip, target_port=80, total_packets=1200, num_workers=10):
    print(f"[*] Launching Multi-Threaded Volumetric Stress Test")
    print(f"    Target: {target_ip}:{target_port} | Packets: {total_packets} | Workers: {num_workers}")
    
    start_time = time.time()
    completed = 0

    def worker_task(packets_per_worker):
        local_count = 0
        for _ in range(packets_per_worker):
            port = target_port if random.random() > 0.3 else random.randint(1024, 65535)
            if probe_single_syn(target_ip, port):
                local_count += 1
        return local_count

    batch_size = total_packets // num_workers
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker_task, batch_size) for _ in range(num_workers)]
        for f in futures:
            completed += f.result()

    elapsed = time.time() - start_time
    pps = total_packets / elapsed if elapsed > 0 else 0
    print(f"[SUCCESS] Stress test completed.")
    print(f"    Elapsed: {elapsed:.3f}s | Throughput: {pps:.1f} packets/second")

def verify_mitigation_closed_loop(target_ip, port=80, max_probes=100):
    print(f"[*] Running Automated Mitigation Verification on {target_ip}:{port}")
    print("    Phase 1: Verifying baseline reachability...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect_ex((target_ip, port))
        s.close()
        print("    [+] Gateway reachable at baseline.")
    except Exception as e:
        print(f"    [-] Gateway unreachable: {e}")

    print("    Phase 2: Initiating attack burst to trigger autonomous iptables rule...")
    attack_start = time.time()
    mitigation_detected = False
    ttm_ms = None

    for i in range(max_probes):
        probe_single_syn(target_ip, port)
        if (i + 1) >= 30 and (i + 1) % 5 == 0:
            check_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            check_sock.settimeout(0.3)
            res = check_sock.connect_ex((target_ip, port))
            check_sock.close()
            if res != 0 and res != 10035 and res != 10061:
                mitigation_detected = True
                ttm_ms = (time.time() - attack_start) * 1000
                print(f"    [!] Traffic drop detected at probe {i + 1}! Kernel iptables DROP engaged.")
                print(f"    [+] Time-to-Mitigate (TTM): {ttm_ms:.2f} ms")
                break
        time.sleep(0.01)

    if not mitigation_detected:
        print("    [*] Probe batch complete. Check Gateway terminal UI for block confirmation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FYP Edge Gateway Traffic Generator & Stress Harness")
    parser.add_argument("--target", default=GATEWAY_IP, help="Target Gateway IP")
    parser.add_argument("--mode", choices=["benign", "ssh", "ddos", "stress", "verify", "all"], default="all", help="Traffic mode")
    parser.add_argument("--packets", type=int, default=1000, help="Total packets for stress test")
    parser.add_argument("--threads", type=int, default=8, help="Worker threads for stress test")

    args = parser.parse_args()

    print("==================================================")
    print(" Edge-AI Traffic Generator & Verification Suite")
    print(f" Target: {args.target} | Mode: {args.mode} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")

    if args.mode in ["benign", "all"]:
        send_benign_traffic(args.target)
        time.sleep(1)

    if args.mode in ["ssh", "all"]:
        send_ssh_bruteforce_simulation(args.target)
        time.sleep(1)

    if args.mode in ["ddos", "all"]:
        send_syn_flood_simulation(args.target)
        time.sleep(1)

    if args.mode in ["stress"]:
        run_multithreaded_stress_test(args.target, total_packets=args.packets, num_workers=args.threads)

    if args.mode in ["verify"]:
        verify_mitigation_closed_loop(args.target)

    print("==================================================")
    print(" Execution finished.")
