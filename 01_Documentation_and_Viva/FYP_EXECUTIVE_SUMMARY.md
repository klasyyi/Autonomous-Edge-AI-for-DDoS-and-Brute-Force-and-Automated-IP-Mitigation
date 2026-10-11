# Project Summary: Autonomous TinyML Edge-Security Gateway

**Prepared for:** Hackathon / Supervisor Review  
**Project Repository / Workspace:** `C:\Users\syara\.gemini\antigravity\scratch\FYP`  
**Full Transcript File:** `FULL_CHAT_TRANSCRIPT.md`  

## 1. Executive Summary
This project develops an autonomous, low-power **Edge-AI Security Gateway** deployed on a Raspberry Pi 4 Model B. Designed for remote enterprise and industrial IoT environments, the gateway performs real-time packet sniffing, flow feature extraction, machine learning classification, and immediate kernel-level firewall mitigation (`iptables`) without requiring internet or cloud connectivity.

## 2. Key Specifications & Performance
- **Hardware:** Raspberry Pi 4 Model B (Quad-core Cortex-A72 @ 1.5GHz, 4GB RAM)
- **Operating System:** Debian GNU/Linux 13 (Trixie) / Linux 6.18 kernel aarch64
- **Dataset:** Canadian Institute for Cybersecurity CIC-IDS-2017 (DDoS and SSH-Patator subsets)
- **Model:** Constrained Random Forest cross-compiled into pure dependency-free Python code via `m2cgen`
- **Inference Latency:** **< 0.10ms (0.08ms)** per flow calculation
- **Classification Accuracy:** **99.98%** on unseen test splits
- **System Resource Footprint:** ~3-5% CPU utilization and ~12% RAM utilization under live sniffing
- **Mitigation Mechanism:** Dynamic Linux `iptables` drop rules with human-readable Explainable AI (XAI) rationale

## 3. Solved Challenges & Adjustments
- **TinyML Inference Optimization:** Eliminated heavy dependencies (scikit-learn/pandas at inference time) to ensure sub-millisecond execution on ARM.
- **Hybrid Layer-4/Layer-7 Defense:** Layer-4 deterministic rate-limiting protects against volumetric SYN floods (`hping3`), reserving the AI for behavioral Application-Layer brute-force attacks (`Hydra`).
- **Explainable AI (XAI):** Real-time console interface displays explicit trigger rationale (e.g., packet rate, Inter-Arrival Times, or model pattern match).
- **Hardened Networking:** Configured static bridge `br0` (`192.168.137.2/24`) with NetworkManager to guarantee headless plug-and-play reliability across reboots.
