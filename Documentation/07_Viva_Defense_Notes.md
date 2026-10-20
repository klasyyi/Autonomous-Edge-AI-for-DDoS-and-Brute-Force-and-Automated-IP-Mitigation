# Viva Defense Notes: Examination Guide and Frequently Asked Questions
## Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation

## 1. Quick Facts Sheet (Memorize Before Defense)

| Parameter | Value / Finding | Details for Panel |
| :--- | :--- | :--- |
| **Multi-Dataset Accuracy** | **96.70%** (Macro F1: 0.9517) | Tested on 23,062 unseen flows from 2017, 2018, and 2019. |
| **IoT Benchmark Accuracy** | **97.18%** | Tested on 26,592 unseen flows from the physical 105-device `CIC-IoT-2023` testbed. |
| **Live Detection Rate** | **100.0%** | Tested across live physical attack injections on the Raspberry Pi 4. |
| **Live False Positive Rate** | **0.0%** (0 false blocks) | Verified under continuous baseline benign HTTP/DNS traffic. |
| **Time-to-Block (TTB)** | **84.21 ms** (SYN Flood) / **62.07 ms** (SSH) | Measured from first attack packet until kernel `iptables DROP` engagement. |
| **Inference Latency** | **0.021 ms** (~47,600 flows/sec) | Pure-Python decision tree execution via `m2cgen` (zero numpy/scikit-learn overhead). |
| **End-to-End Latency** | **0.08 ms to 0.17 ms** | Encompasses raw packet capture, 5-tuple table update, and `iptables` mitigation. |
| **Edge RAM Footprint** | **~24.4 MB RSS** (10.1% to 11.6% OS RAM) | Zero C/C++ machine learning runtime dependencies on the Raspberry Pi. |
| **Zero-Shot Drop (2017 -> 2018)**| **22.64%** (Macro F1: 0.29) | Uncovered testbed bias: model trained solely on 2017 collapsed on 2018 data. |
| **Mitigation Engine** | Automated Linux kernel `iptables` | Dynamic DROP rules with 300s TTL auto-unblock, 500-rule cap, and core IP whitelist. |
| **Deployment Mode** | Headless Linux systemd service | Starts automatically within 25 seconds of power-up (`gateway.service`). |

### Classification Report on 23,062 Unseen Multi-Year Flows
```text
               Precision    Recall    F1-Score    Test Support (Flows)
───────────────────────────────────────────────────────────────────────
BENIGN           0.9975     0.9973     0.9974            5,282
DDoS             0.9987     0.9511     0.9743           14,958
SSH-Patator      0.7941     0.9950     0.8833            2,822
───────────────────────────────────────────────────────────────────────
Accuracy                                0.9670 (96.70%)  23,062
Macro Avg        0.9301     0.9812     0.9517           23,062
Weighted Avg     0.9734     0.9670     0.9685           23,062
```

---

## 2. Key Scientific Narrative: Resolving the Single-Dataset Trap

A central strength of my project defense is demonstrating how I uncovered and resolved **testbed overfitting**:

1. **The Initial 99.98% Result:**  
   When I initially trained my Random Forest solely on `CIC-IDS-2017`, the model reported 99.98% test accuracy.
2. **The Zero-Shot Failure (22.64%):**  
   To verify generalization, I evaluated that 2017 model on unseen traffic from `CSE-CIC-IDS-2018`. The accuracy collapsed to **22.64%**. The model had memorized testbed-specific artifacts (static IP subnets, fixed inter-arrival times, and synthetic background noise) rather than invariant attack behaviors.
3. **The Multi-Dataset Solution:**  
   I designed an 8-feature harmonization pipeline merging multi-year captures across 2017, 2018, and 2019 (115,308 flows). Retraining on this harmonized corpus and validating against physical IoT traffic restored generalized accuracy to **96.70%** (multi-year) and **97.18%** (`CIC-IoT-2023`).

---

## 3. High-Yield Viva Examination Questions and Answers

### Q1: Why did you select Random Forest over Deep Learning (CNN/LSTM/Transformers)?
* **Answer:** Volumetric network attacks require sub-millisecond detection to prevent buffer saturation. Deep neural networks incur heavy matrix multiplications and require large tensor runtimes (PyTorch, TensorFlow) that consume 60% to 95% CPU and hundreds of megabytes of RAM on an ARM Cortex-A72. My constrained Random Forest achieves **96.70% accuracy** with an isolated inference latency of **0.021 ms** and consumes only **~24.4 MB RSS**, providing the optimal trade-off for edge security.

### Q2: Why compile the model with `m2cgen` into pure Python instead of using TensorFlow Lite or ONNX?
* **Answer:** TensorFlow Lite and ONNX Runtime require compiling native C++ shared libraries on ARM Linux, which creates toolchain dependencies, ABI version conflicts, and overhead from tensor memory conversions. `m2cgen` decompiles the decision trees into pure mathematical Python `if/else` branching logic (`pure_rf_multi.py`, 1.05 MB). This runs on bare `python3` with zero external dependencies, provides complete algorithmic auditability, and eliminates the 15 ms numpy array validation delay, achieving a 720x speedup.

### Q3: How did you ensure your high accuracy is not caused by data leakage?
* **Answer:** I enforced three strict controls:
  1. I partitioned the dataset into an 80% training set and a 20% test set *before* performing any data augmentation or balancing.
  2. I applied SMOTE oversampling *exclusively* to the 80% training partition, ensuring synthetic attack vectors never leaked into the validation set.
  3. The 20% test fold consists entirely of untouched natural network traffic.

### Q4: Why use Machine Learning instead of a simple threshold rule or Fail2ban?
* **Answer:** In my baseline benchmark on the unified corpus, a **Static Heuristic Threshold Rule** yielded an accuracy of only 37.11% with a catastrophic **36.01% False Positive Rate (FPR)** on benign traffic. Similarly, Logistic Regression yielded a 44.37% FPR, and a shallow Decision Tree yielded a 13.22% FPR. On a production edge network, falsely blocking 13% to 36% of legitimate users causes severe denial of service. Only the ensemble Random Forest achieved **97.12% accuracy** while suppressing false alarms to **0.19%**, demonstrating that multi-variate non-linear trees are necessary to differentiate legitimate bursts from attacks.

### Q5: How do you handle spoofed IP attacks where an attacker spoofs trusted DNS or gateway IPs?
* **Answer:** I implemented three mitigation safety controls:
  1. **Permanent Whitelist:** Localhost, the default gateway (`192.168.137.1`), core DNS servers (`8.8.8.8`, `1.1.1.1`), and broadcast addresses are whitelisted and never blocked.
  2. **Block Rule TTL (300 Seconds):** Firewall drop rules automatically unblock after 5 minutes, preventing permanent lockout of transient IPs.
  3. **Maximum Rule Cap (500 Rules):** Capped at 500 active `iptables` drop rules to prevent kernel netfilter chain latency degradation.

### Q6: Does your 96.70% accuracy prove zero-shot generalization across all future attacks?
* **Answer:** No. In my Leave-One-Dataset-Out (LODO) experiments, training on 2017+2018 and evaluating on 2019 dropped accuracy significantly because attack vectors evolved (e.g., application-layer HTTP floods in 2017 vs. 0-byte payload SYN floods in 2019). The 96.70% score proves the model is a **Multi-Domain Conditioned Model** that successfully captures the union of transport-layer and application-layer threat profiles when cross-conditioned across heterogeneous captures.

### Q7: What is the difference between your 2.5-hour test and an active volumetric stress test?
* **Answer:** My 2.5-hour test recorded in `history_stress_test_log.csv` is an **Extended Hardware Longevity & Memory Stability Soak Test**. It evaluates daemon stability under continuous physical headless execution, proving that RAM usage remains flat at **10.1% to 11.6%** with zero memory leaks over thousands of seconds of ambient traffic. In contrast, an **Active Volumetric Stress Test** (executed via `simulate_traffic.py --mode stress`) evaluates burst packet ingestion thresholds and kernel mitigation latency under high-rate flood traffic.

### Q8: Why do you report both 0.021 ms and 0.08–0.17 ms for latency?
* **Answer:** This represents a scientific disaggregation of latency across system layers:
  1. **Pure Machine Learning Inference Latency:** **0.021 ms** measures the isolated execution time of my compiled 25-tree Random Forest (`pure_rf_multi.py`) through nested decision logic in memory.
  2. **End-to-End Processing and Mitigation Latency:** **0.08 ms to 0.17 ms** encompasses the entire operational pipeline: raw packet capture, bidirectional flow hash lookup, 8-feature rolling extraction, model classification, and executing the Linux kernel `iptables` drop rule. Both measurements are well within my strict real-time requirement of < 5.0 ms.

### Q9: What are your live physical detection rates, false positive rates, and Time-to-Block (TTB) on real hardware?
* **Answer:** In live physical closed-loop benchmark trials on the Raspberry Pi 4 edge appliance:
  1. **Live Detection Rate:** **100.0%** across both volumetric TCP SYN floods (35 packets) and SSH credential brute force (25 probes).
  2. **Live False Positive Rate:** **0.0%** during baseline benign traffic flows, verifying that legitimate services are never falsely blocked.
  3. **Time-to-Block (TTB):** The system autonomously engaged kernel-level `iptables DROP` within **84.21 ms** for volumetric SYN floods (via Layer-4 rate pre-filtering) and **62.07 ms** for SSH brute force (via TinyML behavioral classification).

---

## 4. The 3 Hardest Engineering Hurdles and My Solutions

### Hurdle 1: The 15 ms Framework Overhead
* **Problem:** Standard Scikit-Learn `.pkl` models required ~15.20 ms per flow on the Raspberry Pi 4 due to numpy array memory allocation and type checking on ARM.
* **Solution:** I cross-compiled the model into pure Python conditional logic (`pure_rf_multi.py`, 1.05 MB). Bypassing the Scikit-Learn framework cut latency to **0.021 ms** (a 720x speedup) with zero third-party dependencies.

### Hurdle 2: Ephemeral Port Randomization During SYN Floods
* **Problem:** In SYN flood attacks, randomized client source ports created thousands of single-packet flow entries, bypassing the 5-packet evaluation threshold.
* **Solution:** I implemented source-IP aggregation for high-rate connection attempts, consolidating randomized packets from the same host into a unified flow context for immediate detection.

### Hurdle 3: Layer 2 vs. Layer 3 Packet Queuing Overhead
* **Problem:** Scapy captures packets at Layer 2 (Data Link layer) before the Linux kernel `iptables` firewall drops them at Layer 3 (Network layer). As a result, the packet sniffer continued processing packets from dropped IPs, wasting CPU cycles.
* **Solution:** I implemented an in-memory early-exit set: `if src_ip in blocked_ips: return`. This drops packets immediately before feature extraction, keeping CPU utilization stable at **0.0% to 0.3%** under routine conditions and ~15% to 20% during peak bursts.
