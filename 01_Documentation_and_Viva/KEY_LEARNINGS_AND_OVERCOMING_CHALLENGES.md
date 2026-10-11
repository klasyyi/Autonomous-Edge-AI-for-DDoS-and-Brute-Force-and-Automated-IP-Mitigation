# Key Learnings & Engineering Challenges Overcome
## Personal & Academic Journey: From Theory to Autonomous Edge-AI

This document records the foundational research insights, hard technical obstacles, and engineering breakthroughs achieved throughout this Final Year Project (FYP). It provides a candid, evidence-backed narrative designed for your **Thesis Chapter 4 & 5 (Implementation & Discussion)** and for direct defense during your **Viva Presentation**.

---

## 🧭 Executive Summary: What Makes This Project Unique?

Building an intrusion detection model in a Python notebook is standard coursework. However, transitioning a machine learning model into an **autonomous, headless, real-time edge security appliance running on physical Raspberry Pi hardware** exposed major real-world engineering bottlenecks that textbook machine learning rarely addresses.

Overcoming these challenges transformed this project from a standard data-science classification exercise into a production-grade **Edge-AI cyber-physical security system**.

```
                        [ REAL-WORLD SYSTEM PIPELINE ]
  [Raw Network Packets] 
          │ (Socket Sniffing)
          ▼
  [Flow Feature Aggregator]  <-- Solved: Sliding Window TTL & Memory Bounds
          │ (0.021 ms / flow)
          ▼
  [Pure-Python Decision Engine] <-- Solved: 0-Dependency Tree Compilation (m2cgen)
          │ (96.70% Cross-Dataset)
          ▼
  [Autonomous Mitigation (iptables)] <-- Solved: Real-Time Closed-Loop Action
          │
          ▼
  [Headless Systemd Daemon] <-- Solved: Zero-Touch Plug-and-Play Resilience
```

---

## 🥊 The 7 Hardest Challenges Overcome

### 1. The "Single-Dataset Illusion" & Zero-Shot Testbed Bias
* **The Hard Problem:**  
  Initially, training our Random Forest classifier solely on the Canadian Institute for Cybersecurity **`CIC-IDS-2017`** dataset achieved a staggering **99.8% accuracy**. However, when our supervisor challenged us to validate this model against unseen data from **`CSE-CIC-IDS-2018`**, the accuracy plummeted catastrophic to **22.64%**.  
* **Root Cause Discovered:**  
  The model had overfitted to synthetic laboratory artifacts specific to the 2017 testbed (fixed IP address ranges, specific packet interval distributions, and synthetic background traffic noise) rather than learning intrinsic, invariant threat signatures.
* **The Breakthrough:**  
  - Constructed a cross-dataset feature harmonization matrix aligning heterogeneous schemas (`Dst Port` $\leftrightarrow$ `Destination Port`, `Tot Fwd Pkts` $\leftrightarrow$ `Total Fwd Packets`, etc.).
  - Harmonized and merged multi-year attack distributions across **CIC-IDS-2017**, **CSE-CIC-IDS-2018**, and **CIC-DDoS-2019** (115,308 flows).
  - Validated the retrained unified model against **`CIC-IoT-2023`**, proving that the model successfully restored generalized detection capability to **96.70%** (multi-year test fold) and **97.18%** (IoT real-device testbed).

---

### 2. The Edge Dependency & Memory Wall (TinyML Compilation)
* **The Hard Problem:**  
  Deploying standard Python data science stacks (`scikit-learn`, `numpy`, `scipy`, `pandas`) onto resource-constrained edge gateways like the Raspberry Pi 4 is fragile and heavy. Installing full ML libraries consumes hundreds of megabytes of disk space, risks C-extension compilation failures on ARM architectures, and consumes excessive base RAM.
* **The Breakthrough:**  
  - Abandoned bulky C-extension runtimes on the edge gateway.
  - Used **`m2cgen`** (Model to Code Generator) to compile our trained Random Forest ensemble directly into raw, dependency-free Python mathematical logic (`pure_rf_multi.py`).
  - **Results:**
    - Edge inference requires **0 external libraries** (runs on plain `python3`).
    - Base RAM footprint reduced to **~24 MB** (only 10.1%–11.6% of total system RAM).
    - Inference latency plummeted to **$0.021\text{ ms}$ per flow** ($\approx 47,600\text{ flows/second}$).

---

### 3. Real-Time Packet Sniffing vs. Offline PCAP Processing
* **The Hard Problem:**  
  In academic research, datasets provide pre-computed statistical features per flow (like `Flow IAT Mean` or `Bwd Packet Length Std`). In the real world, a network card receives individual raw packets (Layer 2 Ethernet frames / Layer 3 IP datagrams), not completed flows!
* **The Breakthrough:**  
  - Designed an asynchronous raw socket sniffer in Python that inspects Layer 3/4 headers in real time.
  - Implemented an in-memory **Rolling Bidirectional Flow Table** keyed by the network 5-tuple:  
    $$\text{Key} = (\text{Src IP}, \text{Dst IP}, \text{Src Port}, \text{Dst Port}, \text{Protocol})$$
  - Handled forward vs. backward packet directionality, calculated moving averages for inter-arrival times (IAT), and enforced an automatic TTL (Time-To-Live) flow eviction policy to prevent memory leaks over days of continuous sniffing.

---

### 4. Autonomous "Plug-and-Play" Headless Daemonization
* **The Hard Problem:**  
  An IoT edge gateway must function as a standalone appliance. In real installations, there is no display, keyboard, or technician typing `python dashboard.py` in an interactive shell. If power fluctuates or the device is unplugged and moved, it must restart seamlessly without human intervention.
* **The Breakthrough:**  
  - Integrated the gateway application into a native Linux **`systemd`** service daemon (`gateway.service`).
  - Configured `Restart=always`, unbuffered logging (`PYTHONUNBUFFERED=1`), and automatic privilege elevation.
  - Verified that plugging in the Raspberry Pi boots straight into continuous packet inspection and mitigation within 25 seconds of power-up.

---

### 5. Extreme Class Imbalance & Data Leakage Prevention
* **The Hard Problem:**  
  In real-world networks (and benchmark datasets), normal (Benign) traffic constitutes 80%–95% of all flows, while stealthy attacks like SSH brute-force (SSH-Patator) make up less than 1%. Naive training produces models with 99% accuracy that simply predict "Benign" 100% of the time, completely missing critical intrusions. Conversely, naively applying SMOTE (Synthetic Minority Over-sampling Technique) across the raw dataset causes **data leakage**, where synthetic copies of test samples leak into the training fold.
* **The Breakthrough:**  
  - Established a strict stratified 80/20 train/test split *prior* to any oversampling.
  - Applied SMOTE strictly to the training fold, balancing the minority classes without contaminating test validation.
  - Achieved a **0.9950 (99.5%) Recall** on SSH brute-force attacks and a **0.9743 F1-score** on DDoS floods without sacrificing Benign traffic accuracy (0.9974 F1).

---

### 6. Bridging Passive Detection to Closed-Loop Autonomous Mitigation
* **The Hard Problem:**  
  Most published NIDS systems are passive—they write an alert to a CSV log file or send an alert email. By the time a human operator reads the alert, a DDoS attack has already saturated the link or a brute-force attacker has compromised the device.
* **The Breakthrough:**  
  - Linked our inference engine directly to the Linux kernel firewall subsystem via **`iptables`**.
  - When the pure-Python classifier detects a malicious flow (DDoS or Brute Force) with high confidence, it immediately issues a kernel-level rule to drop further packets from the offending IP address:
    ```bash
    iptables -I INPUT -s <Attacker_IP> -j DROP
    ```
  - This transformed the gateway from a passive monitoring script into an **autonomous active defense agent**.

---

### 7. Empirical Hardware Verification Over Extended Operation
* **The Hard Problem:**  
  Many academic claims regarding "lightweight" edge models are evaluated purely on desktop simulations rather than physical edge hardware under load.
* **The Breakthrough:**  
  - Established continuous hardware logging on the physical Raspberry Pi 4 over multi-hour intervals.
  - Tracked CPU load, RAM usage, active flow tables, and classification latency every 5 minutes.
  - Proved empirically that under continuous real-time operation, CPU utilization stays between **0.0% and 0.3%**, and RAM remains flat at **10.1%–11.6%**, proving zero memory leakage and true industrial viability.

---

## 🎓 Key Academic & Personal Takeaways

1. **"High accuracy on one dataset is not proof of generalization."**  
   Domain shift and testbed artifacts can deceive even sophisticated neural networks. Real robustness requires cross-dataset training and validation.
2. **"Algorithmic simplicity often beats model complexity at the edge."**  
   A constrained, highly optimized 25-tree Random Forest compiled to pure Python outperformed heavy deep learning models in practical viability by eliminating gigabytes of dependencies and running in microseconds.
3. **"Edge-AI is a systems discipline, not just an ML discipline."**  
   Building an AI security appliance requires mastery of operating system daemons (`systemd`), networking protocols (raw sockets, TCP/IP headers, iptables), memory management, and hardware telemetry alongside machine learning algorithms.
