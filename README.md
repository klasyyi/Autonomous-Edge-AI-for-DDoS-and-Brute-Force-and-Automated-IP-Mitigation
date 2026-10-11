# Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation

> **Author:** Final Year Project (Computer Science / Cyber Security)  
> **Platform:** Raspberry Pi 4 Model B (4GB RAM)  
> **Target Scope:** Autonomous, lightweight Network Intrusion Detection System (NIDS) with closed-loop mitigation for IoT and edge networks.

---

## Executive Summary and Key Results

In this project, I designed and implemented an autonomous Edge-AI security gateway. It protects resource-constrained networks from volumetric DDoS floods and SSH brute-force attacks directly at the local network perimeter.

Rather than relying on heavy deep-learning frameworks or offloading sensitive network telemetry to cloud services, I compiled a multi-dataset Random Forest classifier into pure Python. This allows the system to run on bare Python 3 with zero external machine learning dependencies. The entire system is daemonized using Linux systemd and performs real-time packet inspection, sliding-window flow feature extraction, microsecond inference, and automated kernel-level IP blocking via iptables.

| Metric / Parameter | Value | Details and Significance |
| :--- | :--- | :--- |
| **Multi-Dataset Accuracy** | **96.70%** (Macro F1: 0.9517) | Evaluated on 23,062 unseen flows from CIC-IDS-2017, CSE-CIC-IDS-2018, and CIC-DDoS-2019. |
| **IoT Benchmark Accuracy** | **97.18%** | Evaluated on 26,592 unseen flows from the physical 105-device `CIC-IoT-2023` testbed. |
| **Edge Memory Footprint** | **~24 MB RAM (10.1% of total)** | No C/C++ runtime extensions, numpy, or scikit-learn required on the Raspberry Pi. |
| **Inference Latency** | **0.021 ms / flow (~47,600 flows/sec)** | Compiled pure-Python decision tree execution via m2cgen. |
| **Deployment Mode** | Headless Physical Edge Device | Automatically starts on power-on as a Linux systemd background service (`gateway.service`). |
| **Continuous Telemetry** | 0.0% to 0.3% CPU during live sniffing | Verified across continuous physical hardware execution with zero memory leakage. |

---

## Repository Directory Layout

I organized this workspace into 6 structured directories to ensure full reproducibility, historical tracking, and clear documentation:

```text
FYP/
├── Documentation/       # Technical reports, methodology, file audit, defense notes, and history
├── Publications/        # 12 Peer-reviewed published PDF papers used as academic proof
├── Models/              # Multi-dataset training scripts, compiled decision trees, and model history
├── Datasets/            # Harmonized benchmark datasets (2018, 2019, and 2023)
├── Gateway/             # Production edge gateway engine, terminal UI, and systemd service
├── Testing/             # Traffic simulation scripts, stress test plots, and telemetry history
└── README.md            # Master project documentation
```

---

## Detailed Directory Breakdown

### 1. `Documentation/`
Technical reports, methodology documentation, defense notes, and historical logs:
- [`01_Executive_Summary.md`](Documentation/01_Executive_Summary.md) — Summary brief of system architecture, edge performance, and evaluation metrics.
- [`02_Key_Learnings_and_Challenges.md`](Documentation/02_Key_Learnings_and_Challenges.md) — Personal account of the 7 hardest engineering challenges I solved, including cross-dataset distribution shift, raw socket parsing, and TinyML compilation.
- [`03_Multi_Dataset_Evaluation.md`](Documentation/03_Multi_Dataset_Evaluation.md) — Experimental evidence showing how I identified and eliminated single-dataset testbed bias across 2017, 2018, 2019, and 2023 datasets.
- [`04_Literature_Accuracy_Comparison.md`](Documentation/04_Literature_Accuracy_Comparison.md) — Side-by-side comparison of my model accuracy against published literature across all four benchmark datasets.
- [`05_Literature_Efficiency_Comparison.md`](Documentation/05_Literature_Efficiency_Comparison.md) — Hardware, RAM, and throughput comparison against Jetson Nano, Coral Edge TPU, and standard cloud models.
- [`06_Evaluation_Methodology.md`](Documentation/06_Evaluation_Methodology.md) — Mathematical formulations for Precision, Recall, F1-Score, and data leakage isolation protocols.
- [`07_Viva_Defense_Notes.md`](Documentation/07_Viva_Defense_Notes.md) — Direct technical explanations and Q&A preparation for examination panels.
- [`08_Project_File_Audit.md`](Documentation/08_Project_File_Audit.md) — Comprehensive technical audit of every single file, script, model, and dataset written in Simple Technical English.
- `history/` — Contains labeled raw classification reports and model development history (`history_multi_dataset_raw_report.txt`, `history_model_evolution_log.txt`, `history_findings_and_tradeoffs.txt`, `history_baseline_2017_evaluation.txt`).

### 2. `Publications/`
12 Peer-reviewed and arXiv research papers that I collected as empirical proof for my project defense:
- `Sharafaldin2018_CICIDS2017.pdf` — ICISSP foundation paper introducing the CIC-IDS-2017 dataset.
- `Zhou2019_CICIDS2017_Ensemble.pdf` — Springer research on feature selection and tree ensembles for network security.
- `Karim2020_CSE_CIC_IDS2018_Features.pdf` — Feature selection study on the CSE-CIC-IDS-2018 dataset.
- `Almutairi2021_CICDDoS2019_IoT_ML.pdf` — Evaluation of machine learning algorithms for DDoS on IoT devices using CIC-DDoS-2019.
- `Awotunde2024_CICIoT2023_Lightweight_ML.pdf` — Lightweight zero-trust machine learning on the 105-device CIC-IoT-2023 testbed.
- `Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf` — Resource-aware machine learning and XAI evaluation on CIC-IoT-2023.
- `Ali2025_IEEE_IoT_Edge_IDS.pdf` — IEEE IoT Journal benchmark on edge intrusion detection.
- `Amuthadevi2024_TinyML_IoT_IDS.pdf` — Elsevier TinyML benchmark for energy-constrained IoT hardware.
- `Hafid2024_IEEE_IoT_Edge_IDS.pdf` — IEEE paper on lightweight edge IDS architectures.
- `Mohale2024_Frontiers_XAI_IDS.pdf` — Frontiers in Computer Science benchmark on explainable AI in intrusion detection.
- `Cherukuri2024_Edge_vs_Cloud_AI.pdf` — Comparative study on edge versus cloud AI computing overhead.
- `Ibrahim2026_IoT_ML_NIDS.pdf` — Survey of emerging machine learning NIDS architectures for IoT edge nodes.

### 3. `Models/`
Machine learning training pipelines, model evaluators, and compiled inference engines:
- [`train_multi_dataset.py`](Models/train_multi_dataset.py) — Multi-dataset training pipeline that unifies 2017, 2018, and 2019 flows, applies SMOTE strictly to the training fold, and cross-compiles to pure Python.
- [`pure_rf_multi.py`](Models/pure_rf_multi.py) — My compiled pure-Python Random Forest model (8 features, 3 classes, zero dependencies, 1.05 MB).
- `history/` — Contains previous single-dataset baseline models and evaluators preserved for comparative ablation study (`history_train_v2_single_dataset.py`, `history_pure_rf_v2_model.py`, `history_evaluate_model.py`).

### 4. `Datasets/`
Benchmark dataset samples used for multi-year cross-validation:
- `csecicids2018_sample.csv` (13.5 MB) — Cleaned sample of CSE-CIC-IDS-2018 network flows.
- `cicddos2019_syn_sample.csv` (15.7 MB) — Cleaned sample of CIC-DDoS-2019 volumetric SYN attack traffic.
- `ciciot2023_sample.parquet` (13.4 MB) — High-density traffic sample from the physical 105-device CIC-IoT-2023 testbed.

### 5. `Gateway/`
Production runtime software deployed on the Raspberry Pi edge device:
- [`dashboard.py`](Gateway/dashboard.py) — Core edge engine featuring real-time terminal UI, raw packet sniffer, sliding-window flow builder, TinyML inference, and automated iptables mitigation.
- `pure_rf_multi.py` — Deployed pure-Python inference model on the Raspberry Pi.
- [`gateway.service`](Gateway/gateway.service) — Linux systemd service unit for headless auto-start on boot.
- [`setup_systemd.sh`](Gateway/setup_systemd.sh) — Shell script to install and enable the systemd service on Linux.
- [`check_pi_status.py`](Gateway/check_pi_status.py) — Remote diagnostic script that queries the Pi over SSH for service state, uptime, memory, and firewall rules.
- [`deploy_remote.py`](Gateway/deploy_remote.py) / [`deploy_to_pi.ps1`](Gateway/deploy_to_pi.ps1) — Automated SSH and SCP deployment scripts to transfer and deploy code to the edge device.

### 6. `Testing/`
Edge load generation and telemetry analysis tools:
- [`plot_stress_test.py`](Testing/plot_stress_test.py) — Matplotlib script that reads continuous telemetry and generates time-series charts.
- `stress_test_cpu_ram.png` — Visual evidence showing CPU stability (0.0% to 0.3%) and flatline RAM usage (~10.1% to 11.6%).
- `stress_test_latency_flows.png` — Visual evidence showing microsecond latency and cumulative flow counters.
- [`simulate_traffic.py`](Testing/simulate_traffic.py) — Traffic generator used to test benign sessions, volumetric SYN floods, and SSH brute-force probes against the gateway.
- `history/` — Contains continuous telemetry logs recorded on the Raspberry Pi 4 (`history_stress_test_log.csv`).

---

## Quick Start and Verification Commands

### Check Live Edge Gateway Status
```powershell
python Gateway/check_pi_status.py
```

### Retrain Multi-Dataset Model and Export Pure-Python Code
```powershell
python Models/train_multi_dataset.py
```

### Generate Telemetry Plots from Raspberry Pi Logs
```powershell
python Testing/plot_stress_test.py
```

### Deploy Updated Runtime to Raspberry Pi
```powershell
python Gateway/deploy_remote.py
```

---

## Academic Defense Highlights

1. **Why Pure-Python (`m2cgen`) instead of TensorFlow Lite or PyTorch?**
   - It eliminates over 500 MB of heavy C/C++ dependencies and shared library conflicts on ARM Linux.
   - It runs on standard Python 3 with only ~24 MB RAM overhead.
   - Inference takes only 0.021 ms per network flow.

2. **How I resolved single-dataset testbed bias:**
   - I proved that a model trained strictly on CIC-IDS-2017 collapsed to **22.64% accuracy** on CSE-CIC-IDS-2018 due to domain shift and synthetic testbed artifacts.
   - By creating a unified training corpus across 2017, 2018, and 2019, and validating against `CIC-IoT-2023`, my unified model maintains **96.70%** (multi-year) and **97.18%** (IoT) accuracy.

3. **How the system operates autonomously:**
   - It runs as an independent Linux systemd daemon (`gateway.service`) with `Restart=always`.
   - It boots automatically when plugged into power without requiring a monitor, keyboard, or manual login.
   - When threats are detected, it issues kernel-level iptables rules in real time to isolate attacker IP addresses automatically.
