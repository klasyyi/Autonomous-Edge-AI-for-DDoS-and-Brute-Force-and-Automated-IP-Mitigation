# Project Summary: Autonomous Edge-AI Security Gateway

## 1. Executive Summary

In this project, I developed an autonomous, low-power Edge-AI Security Gateway deployed on a physical Raspberry Pi 4 Model B. Designed for Internet of Things (IoT) and edge computing environments, the gateway performs real-time packet sniffing, sliding-window flow feature extraction, TinyML classification, and automated kernel-level firewall mitigation (`iptables`) without requiring cloud connectivity.

The system operates completely headless as an automated Linux background service (`gateway.service`). It boots into bridged Ethernet (`br0`) automatically when plugged into power and requires zero monitor or keyboard intervention.

---

## 2. Key Specifications and Empirical Performance

- **Hardware Platform:** Raspberry Pi 4 Model B (Quad-core ARM Cortex-A72 @ 1.5 GHz, 4 GB RAM)
- **Operating System:** Debian GNU/Linux (Linux kernel 6.6 aarch64)
- **Benchmark Datasets:** CIC-IDS-2017, CSE-CIC-IDS-2018, CIC-DDoS-2019, and CIC-IoT-2023
- **Classification Engine:** Constrained Random Forest cross-compiled into pure dependency-free Python code via `m2cgen`
- **Compiled Model Size:** 1.05 MB standalone pure-Python file (`pure_rf_multi.py`, zero external dependencies)
- **Model Inference Latency:** 0.021 ms pure ML decision tree evaluation (~47,600 flows/second); 0.08 to 0.17 ms end-to-end packet processing
- **Multi-Dataset Accuracy:** 96.70% (Macro F1: 0.9517) across 23,062 unseen multi-year test flows
- **Modern IoT Accuracy:** 97.18% (Macro F1: 0.9610) evaluated zero-shot on the 105-device physical `CIC-IoT-2023` testbed
- **Physical Detection Rate:** 100.0% mitigation rate across all live physical attack pulses
- **Live False Positive Rate:** 0.000% False Drops (0 drops across 15,381 physical network flows)
- **Physical Time-to-Block (TTB):** 85.72 ms for volumetric TCP SYN floods (DDoS); 62.83 ms for SSH brute-force probing
- **24-Hour Continuous Longevity:** Completed a 24.0-hour diurnal stress soak test (288 discrete 5-minute checkpoints) over physical Ethernet
- **Memory Stability:** Daemon Resident Set Size (RSS) remained flat at 83.54 MB on average ($\sigma = 1.13\text{ MB}$), demonstrating zero memory leaks
- **Thermal Footprint:** Core SoC temperature averaged 38.81 °C (peaking at 41.4 °C under passive cooling), more than 38 °C below the 80.0 °C throttling limit
- **CPU Utilization:** Averaged 25.61% under continuous physical traffic load, preserving 74.4% compute headroom
- **Fail-Safe Mitigations:** Automated Linux kernel `iptables DROP` rules with permanent infrastructure whitelisting, 300-second block TTL auto-unblock, and 500-rule table ceilings
- **Headless Boot Automation:** Self-healing Linux `systemd` daemon begins packet capture within 25 seconds of power-up

---

## 3. Core Engineering Achievements

1. **TinyML Optimization Without C++ Dependencies:**  
   I eliminated all heavy machine learning frameworks (no scikit-learn, numpy, or tensorflow at inference time). Compiling the decision trees into pure Python conditional logic reduced inference latency from 15.20 ms to 0.021 ms (a 720x speedup) with only 83.5 MB RAM footprint.

2. **Resolving Cross-Dataset Overfitting:**  
   I uncovered that a model trained solely on 2017 data suffered a catastrophic collapse to 22.64% accuracy when evaluated on 2018 data due to single-testbed bias. By designing an invariant 8-feature representation across 2017, 2018, and 2019 data (115,308 flows), I restored generalized accuracy to 96.70% and verified it zero-shot on 2023 IoT traffic at 97.18%.

3. **Empirical Baseline Superiority:**  
   I benchmarked the ensemble Random Forest against heuristic threshold rules and linear models. A static threshold rule generated a 36.01% False Positive Rate on benign traffic. My Random Forest reduced false alarms to 0.19% on offline data and 0.000% on live physical hardware.

4. **Closed-Loop Physical Mitigation in Under 100 ms:**  
   Unlike published academic papers that only test passive model speed on saved CSV files, I built an end-to-end inline defense appliance over physical Ethernet. The appliance ingests live packet bursts, evaluates flows, and executes kernel firewall drop rules within 85.72 ms for DDoS and 62.83 ms for SSH brute force.

5. **24-Hour Diurnal Hardware Soak Test:**  
   I verified operational stability by running the system for 24 continuous hours under physical network load, demonstrating zero memory leaks, cool temperatures, and zero service interruptions.
