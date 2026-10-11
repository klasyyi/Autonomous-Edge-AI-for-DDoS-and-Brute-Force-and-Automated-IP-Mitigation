# FYP Results & VIVA Defense Notes: Autonomous Edge-AI Gateway

## 1. AI Accuracy & Performance (The Proof)

**Overall Accuracy:** 99.98% (Evaluated on a 20% unseen test split of 132,685 flows)

### Detailed Classification Metrics
| Traffic Class | Precision | Recall | F1-Score | Support (Flows) |
| :--- | :--- | :--- | :--- | :--- |
| **BENIGN** | 1.00 (100%) | 1.00 (100%) | 1.00 | 106,071 |
| **DDoS (SYN/HTTP Floods)** | 1.00 (100%) | 1.00 (100%) | 1.00 | 25,478 |
| **SSH-Patator (Brute-Force)** | 1.00 (100%) | 1.00 (100%) | 1.00 | 1,136 |

### Real-World Gateway Performance
*   **Inference Latency:** ~0.08ms (Shattering the <5ms objective)
*   **Hardware Efficiency:** CPU stable at ~20% during sustained volumetric floods on Raspberry Pi 4.
*   **Mitigation:** 100% autonomous Kernel-level drop via `iptables`.

---

## 2. Methodology: How We Achieved It

If examiners ask how the model achieved 99.98% accuracy on low-power hardware, use these points:

*   **Multi-Threat Datasets:** Combined the Friday (DDoS) and Tuesday (SSH-Patator) datasets from CIC-IDS-2017 to train a robust, multi-class model.
*   **Aggressive Feature Selection:** Distilled 84 standard network features down to the 8 most mathematically distinct features (e.g., *Fwd Packet Length Mean*, *Destination Port*). This completely eliminated background noise and significantly reduced compute overhead on the Pi.
*   **Class Balancing (SMOTE):** Real-world network traffic is 99% BENIGN. Without balancing, the AI would be inherently biased. We applied the SMOTE algorithm to synthesize minority attack classes (SSH/DDoS) before training to ensure the AI learned attack signatures equally.
*   **Constrained Architecture:** Enforced `n_estimators=20` and `max_depth=10` on the Random Forest. This ensured the model remained small enough (TinyML) to run entirely in the Raspberry Pi's RAM without swapping.

---

## 3. Major Engineering Hurdles & Solutions (VIVA Talking Points)

Examiners love when you face hurdles and solve them. Use these three major challenges to prove your engineering capability:

### Hurdle 1: The 15ms Framework Bottleneck
*   **The Problem:** Initial live testing showed ~15ms inference latency, which failed the <5ms objective. Investigation revealed that the AI math was fast, but the Python `scikit-learn` framework's "input-validation checks" caused massive overhead on the Raspberry Pi's ARM processor.
*   **The Solution:** Executed Model Compilation. We decompiled the Random Forest binary `.pkl` model into pure, raw Python `if/else` logic using `m2cgen`. By bypassing `scikit-learn` entirely, latency dropped 150x to just **0.08ms**.

### Hurdle 2: The State-Exhaustion Bypass
*   **The Problem:** During live testing against `hping3`, we realized the attacker was dynamically randomizing their source port for every packet. Because standard stateful firewalls track flows by ports, the gateway saw 30,000 unique 1-packet flows instead of one massive flow, allowing the attacker to completely bypass the AI's 5-packet evaluation threshold.
*   **The Solution:** Adjusted the flow-tracking architecture. For volumetric floods, grouping by pure IP addresses defeated the state-exhaustion attempt, forcing the AI to evaluate the attacker globally. 

### Hurdle 3: The Scapy Packet Queuing Delay (Layer 2 vs Layer 3)
*   **The Problem:** During a massive flood, the dashboard was taking 3-4 minutes to process packets *even after* the attacker was successfully blocked. We discovered this is a Linux Networking quirk: Scapy sniffs packets at Layer 2 (Data Link), which means it still processes packets before `iptables` deletes them at Layer 3 (Network). Scapy was pegging the CPU doing heavy math on dead packets.
*   **The Solution:** Implemented a User-Space "Early-Exit Bypass". By adding `if src_ip in blocked_ips: return` at the very top of the script, the CPU instantly trashes dropped packets with zero math overhead, allowing the Pi to survive massive volumetric floods without crashing.
