# Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation
## Executive Summary and Key Results

In this project, I designed and implemented an autonomous Edge-AI security gateway. It protects resource-constrained networks from volumetric TCP SYN floods and SSH brute-force attacks directly at the local network perimeter.

Rather than relying on heavy deep-learning frameworks or offloading sensitive network telemetry to cloud services, I compiled a multi-dataset Random Forest classifier into pure Python. This allows the system to run on bare Python 3 with zero external machine learning dependencies. The entire system is daemonized using Linux systemd and performs real-time packet inspection, sliding-window flow feature extraction, microsecond inference, and automated kernel-level IP blocking via iptables.

| Metric / Parameter | Value | Details and Significance |
| :--- | :--- | :--- |
| **Multi-Dataset Accuracy** | **96.70%** (Macro F1: 0.9517) | Evaluated on 23,062 unseen flows from CIC-IDS-2017, CSE-CIC-IDS-2018, and CIC-DDoS-2019. |
| **IoT Benchmark Accuracy** | **97.18%** | Evaluated on 26,592 unseen flows from the physical 105-device `CIC-IoT-2023` testbed. |
| **Live Detection Rate** | **100.0%** | Verified across physical attack injections on the live Raspberry Pi 4 edge appliance. |
| **Live False Positive Rate** | **0.0%** (0 false drops) | Verified under continuous baseline benign HTTP/DNS traffic with zero service disruption. |
| **Time-to-Block (TTB)** | **84.21 ms** (SYN) / **62.07 ms** (SSH) | Physical elapsed time from first attack packet until kernel-level `iptables DROP` engagement. |
| **Edge Memory Footprint** | **~24.4 MB RSS daemon** (10.1%–11.6% total OS RAM) | Daemon process consumes ~24.4 MB RSS; total OS RAM is ~400–460 MB on the 4 GB Raspberry Pi 4. No C/C++ ML runtime extensions, numpy, or scikit-learn required on edge. |
| **Inference Latency** | **0.021 ms pure ML** (~47,600 flows/sec) | 0.021 ms per flow pure decision tree evaluation; 0.08–0.17 ms end-to-end packet capture and feature extraction pipeline. |
| **Deployment Mode** | Headless Physical Edge Device | Automatically starts on power-on as a Linux systemd background service (`gateway.service`). |
| **Continuous Telemetry** | 0.0% to 0.3% CPU during baseline sniffing | Verified across extended physical hardware execution with zero daemon memory leakage. |

---

## Repository Directory Layout

I organized this workspace into structured directories to ensure full reproducibility, historical tracking, and clear documentation:

```text
FYP/
├── Documentation/       # Technical reports, methodology, file audit, defense notes, and history
├── Publications/        # 12 Peer-reviewed published PDF papers and REFERENCES.md bibliography
├── Models/              # Multi-dataset training scripts, LODO evaluators, compiled trees, and history
├── Datasets/            # Harmonized benchmark datasets (2018, 2019, and 2023)
├── Gateway/             # Production edge gateway engine, terminal UI, and systemd service
├── Testing/             # Live closed-loop attack benchmarks, traffic generators, and stress plots
├── tests/               # Automated unit, latency, flow feature, and fail-safe mitigation test suite
├── LICENSE              # MIT License
├── requirements.txt     # Python environment dependencies
└── README.md            # Master project documentation
```

---

## Detailed Directory Breakdown

### 1. `Documentation/`
Technical reports, methodology documentation, defense notes, and historical logs:
- [`01_Executive_Summary.md`](Documentation/01_Executive_Summary.md) — Summary brief of system architecture, edge performance, and evaluation metrics.
- [`02_Key_Learnings_and_Challenges.md`](Documentation/02_Key_Learnings_and_Challenges.md) — Personal account of the 7 hardest engineering challenges I solved, including cross-dataset distribution shift, raw socket parsing, and TinyML compilation.
- [`03_Multi_Dataset_Evaluation.md`](Documentation/03_Multi_Dataset_Evaluation.md) — Experimental evidence showing how I analyzed and reduced single-dataset testbed bias across 2017, 2018, 2019, and 2023 datasets, including Leave-One-Dataset-Out (LODO) domain shift analysis.
- [`04_Literature_Accuracy_Comparison.md`](Documentation/04_Literature_Accuracy_Comparison.md) — Side-by-side comparison of my model accuracy against published literature across all four benchmark datasets.
- [`05_Literature_Efficiency_Comparison.md`](Documentation/05_Literature_Efficiency_Comparison.md) — Hardware, RAM, and throughput comparison against Jetson Nano, Coral Edge TPU, and standard cloud models.
- [`06_Evaluation_Methodology.md`](Documentation/06_Evaluation_Methodology.md) — Mathematical formulations for Precision, Recall, F1-Score, baseline classifier comparisons, and live closed-loop physical mitigation metrics.
- [`07_Viva_Defense_Notes.md`](Documentation/07_Viva_Defense_Notes.md) — Direct technical explanations and Q&A preparation for examination panels covering threat models, anti-spoofing mitigation, and latency analysis.
- [`08_Project_File_Audit.md`](Documentation/08_Project_File_Audit.md) — Comprehensive technical audit of every single file, script, model, and dataset written in Simple Technical English.
- `history/` — Contains labeled raw classification reports and model development history (`history_multi_dataset_raw_report.txt`, `history_lodo_and_baselines.txt`, `history_live_mitigation_benchmark.txt`, `history_model_evolution_log.txt`, `history_findings_and_tradeoffs.txt`, `history_baseline_2017_evaluation.txt`).

### 2. `Publications/`
12 Peer-reviewed and arXiv research papers that I collected as empirical proof for my project defense:
- [`REFERENCES.md`](Publications/REFERENCES.md) — Comprehensive academic bibliography containing complete bibliographic metadata, DOIs, publication venues, and BibTeX citations for all 12 referenced papers.
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
- [`evaluate_lodo_and_baselines.py`](Models/evaluate_lodo_and_baselines.py) — Standalone validation suite that evaluates Leave-One-Dataset-Out (LODO) zero-shot cross-validation and benchmarks Random Forest against static rules, Logistic Regression, and shallow Decision Trees.
- [`pure_rf_multi.py`](Models/pure_rf_multi.py) — My compiled pure-Python Random Forest model (8 features, 3 classes, zero dependencies, 1.05 MB).
- `history/` — Contains previous single-dataset baseline models and evaluators preserved for comparative ablation study (`history_train_v2_single_dataset.py`, `history_pure_rf_v2_model.py`, `history_evaluate_model.py`).

### 4. `Datasets/`
Benchmark dataset samples used for multi-year cross-validation:
- `csecicids2018_sample.csv` (13.5 MB) — Cleaned sample of CSE-CIC-IDS-2018 network flows.
- `cicddos2019_syn_sample.csv` (15.7 MB) — Cleaned sample of CIC-DDoS-2019 volumetric SYN attack traffic.
- `ciciot2023_sample.parquet` (13.4 MB) — High-density traffic sample from the physical 105-device CIC-IoT-2023 testbed.

### 5. `Gateway/`
Production runtime software deployed on the Raspberry Pi edge device:
- [`dashboard.py`](Gateway/dashboard.py) — Core edge engine featuring real-time terminal UI, raw packet sniffer, auto-detected bridge (`br0`), sliding-window flow builder, TinyML inference, active whitelist, flow TTL eviction, and automated iptables mitigation with auto-unblock timers.
- `pure_rf_multi.py` — Deployed pure-Python inference model on the Raspberry Pi.
- [`gateway.service`](Gateway/gateway.service) — Linux systemd service unit for headless auto-start on boot.
- [`setup_systemd.sh`](Gateway/setup_systemd.sh) — Shell script to install and enable the systemd service on Linux.
- [`check_pi_status.py`](Gateway/check_pi_status.py) — Remote diagnostic script that queries the Pi over SSH for service state, uptime, memory, and firewall rules.
- [`deploy_remote.py`](Gateway/deploy_remote.py) / [`deploy_to_pi.ps1`](Gateway/deploy_to_pi.ps1) — Automated SSH and SCP deployment scripts to transfer and deploy code to the edge device.

### 6. `Testing/`
Edge load generation, live mitigation benchmarks, and telemetry analysis tools:
- [`bench_live_mitigation.py`](Testing/bench_live_mitigation.py) — Automated closed-loop benchmark that dispatches real-time attack payloads across the bridge and measures exact physical Time-to-Block (TTB) and iptables rule engagement.
- [`plot_stress_test.py`](Testing/plot_stress_test.py) — Matplotlib script that reads continuous telemetry and generates publication-grade time-series charts.
- `stress_test_cpu_ram.png` — Visual evidence showing CPU stability (0.0% to 0.3%) and flatline RAM usage (~10.1% to 11.6%) during extended longevity soak execution.
- `stress_test_latency_flows.png` — Visual evidence showing microsecond latency and cumulative flow counters.
- [`simulate_traffic.py`](Testing/simulate_traffic.py) — Multi-threaded traffic generator and stress testing harness supporting benign sessions, volumetric SYN floods, SSH brute force, and high-throughput load generation.
- `history/` — Contains continuous telemetry logs recorded on the Raspberry Pi 4 (`history_stress_test_log.csv`).

### 7. `tests/`
Automated unit, latency, and fail-safe safety verification suite:
- [`tests/test_model.py`](tests/test_model.py) — Validates pure-Python decision tree predictions across Benign, DDoS, and SSH-Patator traffic, checks zero-dependency imports, and asserts sub-0.1 ms latency constraints.
- [`tests/test_mitigation_safety.py`](tests/test_mitigation_safety.py) — Validates fail-safe anti-spoofing mitigation: infrastructure whitelist protection, 300-second block TTL auto-unblock, 500-rule ceiling cap, and 60-second sliding-window flow table eviction.
- [`tests/test_flow_features.py`](tests/test_flow_features.py) — Validates real-time 8-feature vector extraction, mathematical formulas, and safe division handling under zero-packet edge cases.

---

## Quick Start and Verification Commands

### Run Automated Unit and Safety Tests
```powershell
python -m unittest discover tests
```

### Run Live Closed-Loop Hardware Attack Benchmark
```powershell
python Testing/bench_live_mitigation.py
```

### Check Live Edge Gateway Status
```powershell
python Gateway/check_pi_status.py
```

### Retrain Multi-Dataset Model and Export Pure-Python Code
```powershell
python Models/train_multi_dataset.py
```

### Evaluate LODO and Baseline Classifiers
```powershell
python Models/evaluate_lodo_and_baselines.py
```

### Generate Telemetry Plots from Raspberry Pi Logs
```powershell
python Testing/plot_stress_test.py
```

---

## Key Technical Design Decisions

1. **Why Pure-Python (`m2cgen`) instead of TensorFlow Lite or PyTorch?**
   - Eliminates over 500 MB of heavy C/C++ dependencies and shared library conflicts on ARM Linux.
   - Runs on standard Python 3 with only ~24.4 MB RSS process overhead.
   - Inference requires only 0.021 ms per network flow.

2. **How I addressed single-dataset testbed bias:**
   - I demonstrated that a model trained strictly on CIC-IDS-2017 collapsed to **22.64% accuracy** on CSE-CIC-IDS-2018 due to domain shift and synthetic testbed artifacts.
   - By creating a unified training corpus across 2017, 2018, and 2019, and validating against `CIC-IoT-2023`, my unified model maintains **96.70%** (multi-year) and **97.18%** (IoT) accuracy.
   - Full domain shift analysis and Leave-One-Dataset-Out (LODO) validation are documented in [`03_Multi_Dataset_Evaluation.md`](Documentation/03_Multi_Dataset_Evaluation.md).

3. **Autonomous Edge Operation and Fail-Safe Mitigation:**
   - Runs as an independent Linux systemd daemon (`gateway.service`) with `Restart=always`.
   - Boots automatically when plugged into power without requiring a monitor, keyboard, or manual login.
   - To prevent Denial-of-Service via IP spoofing, the mitigation engine enforces permanent IP whitelisting for core infrastructure, a 300-second block expiration timer (TTL), a maximum rule ceiling of 500 rules, and sliding-window flow eviction.
   - Physical closed-loop benchmarks demonstrated a **100.0% live detection rate**, **0.0% false positive rate**, and sub-100 ms kernel mitigation (**84.21 ms** for SYN floods; **62.07 ms** for SSH brute force).
   - Detailed viva defense responses, threat models, and architectural boundaries are compiled in [`07_Viva_Defense_Notes.md`](Documentation/07_Viva_Defense_Notes.md).
