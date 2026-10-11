# Viva Defense Notes and Experimental Results
## 1. Model Accuracy and Operational Performance

In my final evaluations, the gateway classifier achieved the following empirical results:

- **Overall Accuracy:** 99.98% (Evaluated on a 20% unseen test split of 132,685 flows)
- **Average Inference Latency:** ~0.08 ms per flow (well within my project requirement of < 5.0 ms)
- **CPU Utilization:** Stable at ~20% under sustained volumetric flooding
- **Autonomous Mitigation:** 100% automated kernel-level dropping via Linux `iptables`

### Detailed Classification Metrics
| Traffic Class | Precision | Recall | F1-Score | Support (Flows) |
| :--- | :--- | :--- | :--- | :--- |
| **BENIGN** | 1.00 (100%) | 1.00 (100%) | 1.00 | 106,071 |
| **DDoS (SYN/HTTP Floods)** | 1.00 (100%) | 1.00 (100%) | 1.00 | 25,478 |
| **SSH-Patator (Brute-Force)** | 1.00 (100%) | 1.00 (100%) | 1.00 | 1,136 |

---

## 2. Methodology: How I Achieved These Results

When designing the machine learning pipeline for resource-constrained hardware, I made four specific architectural decisions:

1. **Multi-Threat Dataset Integration:**  
   I combined Friday (DDoS) and Tuesday (SSH-Patator) captures from the CIC-IDS-2017 benchmark to train a robust, multi-class model capable of handling diverse attack patterns.

2. **Feature Space Distillation:**  
   I reduced the 84 standard network features down to 8 core features (e.g., `Destination Port`, `Fwd Packet Length Mean`, `SYN Flag Count`). This eliminated background noise and significantly lowered computation overhead on the Raspberry Pi.

3. **Pre-Training Class Balancing via SMOTE:**  
   Because raw network datasets are heavily dominated by benign traffic (>99%), an unmitigated model would be biased. I partitioned the dataset into 80% train and 20% test splits before applying SMOTE, ensuring synthetic samples remained strictly within the training set and eliminating data leakage.

4. **Constrained Model Architecture:**  
   I configured the Random Forest classifier with `n_estimators = 20` and `max_depth = 10`. This kept memory usage small enough to run fully within RAM on the Raspberry Pi without page swapping.

---

## 3. Major Engineering Hurdles and My Solutions

During development and physical testbed deployment, I resolved three major engineering challenges:

### Hurdle 1: The 15 ms Framework Overhead
- **The Problem:** In my initial live tests on the Raspberry Pi 4, inference latency was approximately 15 ms per flow, exceeding my project requirement of < 5 ms. Profiling showed that the decision tree mathematics was fast, but Scikit-Learn internal validation checks and NumPy conversions introduced substantial overhead on ARM.
- **My Solution:** I used `m2cgen` to compile the trained Scikit-Learn Random Forest model into native Python conditional statements (`pure_rf_v2.py`). Bypassing the Scikit-Learn framework cut inference latency from 15 ms down to 0.08 ms (a 180x speedup), with zero external dependencies.

### Hurdle 2: State-Exhaustion Bypass During Volumetric Flooding
- **The Problem:** When running SYN flood tests using `hping3`, the attack tool randomized the client source port on every packet. Traditional flow tracking relies on a 5-tuple (source IP, source port, destination IP, destination port, protocol). Because every packet had a new source port, the gateway created thousands of single-packet flow entries instead of one cumulative flow, which allowed the attacker to bypass my 5-packet evaluation threshold.
- **My Solution:** I adapted the flow-tracking architecture. For volumetric flood mitigation, I aggregated packets at the source IP level rather than per ephemeral port. This aggregated all randomized packets from the attacking host into a unified flow context, allowing the model to detect and block the attack within the first 5 packets.

### Hurdle 3: Layer 2 vs. Layer 3 Packet Queuing in Scapy
- **The Problem:** During high-rate packet floods, the dashboard continued processing packets for 3 to 4 minutes even after `iptables` had already dropped the attacking IP at the Linux kernel level. This occurred because Scapy operates via raw sockets at Layer 2 (Data Link layer), capturing packets before the Linux kernel `iptables` firewall drops them at Layer 3 (Network layer). Scapy was consuming CPU cycles analyzing dropped traffic.
- **My Solution:** I implemented an in-memory early-exit filter in user space. By maintaining a set of currently blocked IP addresses and checking `if src_ip in blocked_ips: return` as the first step of the packet callback, the packet is instantly discarded before extracting features or updating flow tables. This allowed the gateway to sustain high-rate floods at ~20% CPU utilization without crashing.
