# Project Summary: Autonomous Edge-AI Security Gateway

## 1. Executive Summary

In this project, I developed an autonomous, low-power Edge-AI Security Gateway deployed on a Raspberry Pi 4 Model B. Designed for Internet of Things (IoT) and edge computing environments, the gateway performs real-time packet sniffing, sliding-window flow feature extraction, TinyML classification, and automated kernel-level firewall mitigation (`iptables`) without requiring cloud connectivity.

---

## 2. Key Specifications and Performance

- **Hardware Platform:** Raspberry Pi 4 Model B (Quad-core Cortex-A72 @ 1.5GHz, 4GB RAM)
- **Operating System:** Debian GNU/Linux (Linux kernel aarch64)
- **Benchmark Datasets:** CIC-IDS-2017, CSE-CIC-IDS-2018, CIC-DDoS-2019, and CIC-IoT-2023
- **Classification Engine:** Constrained Random Forest cross-compiled into pure dependency-free Python code via `m2cgen`
- **Compiled Model Size:** 1.05 MB standalone pure-Python file (`pure_rf_multi.py`, zero external dependencies)
- **Inference Latency:** 0.021 ms pure ML decision tree evaluation (~47,600 flows/second); 0.08 to 0.17 ms end-to-end packet sniffing, feature extraction, and classification pipeline
- **Multi-Dataset Accuracy:** 96.70% across 23,062 unseen multi-year test flows
- **IoT Benchmark Accuracy:** 97.18% evaluated on the 105-device physical `CIC-IoT-2023` testbed
- **System Memory Footprint:** ~24.4 MB RSS daemon footprint (~400 to 460 MB total OS RAM, 10.1% to 11.6% of 4 GB Raspberry Pi 4)
- **Mitigation Mechanism:** Dynamic Linux kernel `iptables` drop rules executed autonomously upon threat detection, protected by infrastructure whitelists, 300s auto-unblock timers, and rule ceilings
- **Daemonization:** Headless Linux `systemd` background service (`gateway.service`) with auto-start on device power-up

---

## 3. Engineering Achievements

- **TinyML Optimization:** I eliminated all heavy C/C++ machine learning runtime dependencies (no scikit-learn, numpy, or tensorflow at inference time), enabling sub-millisecond execution on resource-constrained ARM hardware.
- **Cross-Dataset Generalization:** I identified and resolved single-dataset testbed bias (where a model trained solely on 2017 data dropped to 22.64% on 2018 data) by harmonizing features across 2017, 2018, and 2019 data and validating on 2023 IoT traffic.
- **Empirical Baseline Superiority:** I benchmarked the Random Forest model against static threshold heuristics and linear classifiers, demonstrating that static rules produce a 36.01% False Positive Rate on legitimate benign traffic, whereas my ensemble model reduces false alarms to 0.19% (a 70-fold reduction).
- **Hybrid Volumetric and Behavioral Protection:** I coupled Layer-4 rate-limiting with behavioral TinyML detection to handle both high-volume SYN floods and stealthy Application-Layer brute-force attacks.
- **Fail-Safe Autonomous Mitigation:** To prevent Denial of Service via IP spoofing, I incorporated permanent whitelisting for core gateway and DNS infrastructure, an automated 300-second block TTL auto-unblock mechanism, and a strict 500-rule iptables ceiling cap.
- **Headless Plug-and-Play Operation:** I configured the gateway as a self-healing Linux service that automatically begins sniffing and mitigation within 25 seconds of power connection.
