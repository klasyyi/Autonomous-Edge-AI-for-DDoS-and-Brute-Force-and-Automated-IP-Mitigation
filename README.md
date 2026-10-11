# Edge-Native IoT Intrusion Detection System (FYP Master Workspace)

> **Final Year Project (FYP)**: Lightweight, Pure-Python Machine Learning Network Intrusion Detection System for Resource-Constrained Edge Gateways (Raspberry Pi 4)  
> **Target Completion:** Week 8 | **Current Phase:** Week 6 Milestone (Multi-Dataset Harmonization & Edge Deployment Complete)

---

## 📊 Executive Summary & Key Results

| Metric / Parameter | Value | Reference / Status |
| :--- | :--- | :--- |
| **Multi-Dataset Accuracy** | **96.70%** (Macro F1: 0.9517) | Tested on 23,062 unseen flows (CIC-IDS-2017 + CSE-CIC-IDS-2018 + CIC-DDoS-2019) |
| **IoT Benchmark Accuracy** | **97.18%** | Evaluated on 26,592 flows from `CIC-IoT-2023` |
| **Supervisor Threshold** | $> 80.0\%$ | **Exceeded by +16.70%** |
| **Edge Memory Footprint** | **~24 MB RAM (10.1% total)** | Zero C/C++ or heavy ML runtime (`numpy`/`scikit-learn` free) |
| **Inference Latency** | **$0.021\text{ ms}$ / flow ($\sim 47,600\text{ flows/sec}$)** | Compiled tree traversal via pure Python (`m2cgen`) |
| **Edge Hardware** | Raspberry Pi 4 Model B (4GB) | Auto-starts on power-on via `systemd` daemon (`gateway.service`) |
| **Edge Telemetry** | 0.0% – 0.3% CPU during idle/sniffing | Verified over 1.5+ hours continuous logging with zero memory leaks |

---

## 📂 Repository Directory Layout

The workspace has been organized into 7 structured directories to ensure zero data loss, reproducible evaluations, and structured documentation for your thesis and viva presentation:

```text
FYP/
├── 01_Documentation_and_Viva/       # Academic reports, viva defense prep, methodology & file audit
├── 02_Publications_Proof/           # 12 Peer-reviewed published papers (IEEE, Frontiers, etc.) for defense
├── 03_Models_and_Training/          # Training pipelines, compiled pure-Python tree models & evaluators
├── 04_Dataset_Benchmarks/           # Harmonized benchmark datasets (CSE-CIC-IDS2018, CIC-DDoS2019, CIC-IoT2023)
├── 05_Gateway_Runtime/              # Production edge gateway code, curses dashboard & systemd service
├── 06_Testing_and_Telemetry/        # Traffic simulation scripts, stress test logs & performance plots
├── 07_Transcripts_and_History/      # Complete project history, chat logs, and 56 media attachments
├── README.md                        # Master project index & quickstart guide (this file)
└── AGENTS.md                        # AI pair-programming and engineering guidelines
```

---

## 📁 Detailed Directory Breakdown

### 1. `01_Documentation_and_Viva/`
Comprehensive documentation, viva preparation cheat sheets, and academic reports:
- [`PROJECT_FILE_AUDIT.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/PROJECT_FILE_AUDIT.md) — Comprehensive technical audit of every single file, script, model, and dataset in Simple Technical English.
- [`KEY_LEARNINGS_AND_OVERCOMING_CHALLENGES.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/KEY_LEARNINGS_AND_OVERCOMING_CHALLENGES.md) — Comprehensive narrative of technical hurdles, TinyML compilation, socket sniffing, and lessons learned.
- [`FYP_EXECUTIVE_SUMMARY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/FYP_EXECUTIVE_SUMMARY.md) — 1-page executive brief covering architecture, edge performance, and academic metrics.
- [`MULTI_DATASET_EVALUATION.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/MULTI_DATASET_EVALUATION.md) — Rigorous proof resolving single-dataset testbed bias using 2017, 2018, 2019, and 2023 datasets.
- [`LITERATURE_COMPARISON_ACCURACY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/LITERATURE_COMPARISON_ACCURACY.md) — Side-by-side comparison against published papers across all 4 datasets.
- [`LITERATURE_COMPARISON_EFFICIENCY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/LITERATURE_COMPARISON_EFFICIENCY.md) — Hardware, RAM, and throughput comparison against TinyML, Edge TPU, and Jetson Nano.
- [`EVALUATION_METHODOLOGY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/EVALUATION_METHODOLOGY.md) — Mathematical formulations for Precision, Recall, F1, and memory metrics.
- [`VIVA_Results_and_Notes.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/VIVA_Results_and_Notes.md) — Direct Q&A talking points for examiners and viva defense.
- `Findings_and_Tradeoffs.txt`, `Model_Evolution_and_Accuracy.txt`, `multi_dataset_evaluation_report.txt` — Historical engineering logs.

### 2. `02_Publications_Proof/`
12 Original peer-reviewed / arXiv publications used as empirical proof for viva defense:
- `Sharafaldin2018_CICIDS2017.pdf` — ICISSP foundation paper introducing the CIC-IDS-2017 dataset.
- `Zhou2019_CICIDS2017_Ensemble.pdf` — Ensemble feature selection and tree-based classification (Springer).
- `Karim2020_CSE_CIC_IDS2018_Features.pdf` — Optimal feature selection and evaluation on **CSE-CIC-IDS-2018** (arXiv).
- `Almutairi2021_CICDDoS2019_IoT_ML.pdf` — Machine learning evaluation for DDoS on IoT devices using **CIC-DDoS-2019** (arXiv).
- `Awotunde2024_CICIoT2023_Lightweight_ML.pdf` — Zero-trust lightweight ML on **CIC-IoT-2023** real device testbed (arXiv).
- `Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf` — Resource-aware ML/XAI intrusion detection on **CIC-IoT-2023** (arXiv).
- `Ali2025_IEEE_IoT_Edge_IDS.pdf` — IEEE IoT Journal benchmark on edge intrusion detection.
- `Amuthadevi2024_TinyML_IoT_IDS.pdf` — Elsevier TinyML-based IoT security benchmarks.
- `Hafid2024_IEEE_IoT_Edge_IDS.pdf` — Lightweight edge IDS architectures (IEEE).
- `Mohale2024_Frontiers_XAI_IDS.pdf` — Frontiers in Computer Science benchmark on CIC-IDS-2017.
- `Cherukuri2024_Edge_vs_Cloud_AI.pdf` — Edge vs Cloud AI resource consumption analysis.
- `Ibrahim2026_IoT_ML_NIDS.pdf` — Emerging NIDS models for IoT edge nodes.

### 3. `03_Models_and_Training/`
Model training, feature engineering, and cross-compilation code:
- [`train_multi_dataset.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/03_Models_and_Training/train_multi_dataset.py) — Multi-dataset training pipeline (harmonizes 2017, 2018, and 2019 data; cross-compiles to pure Python via `m2cgen`).
- [`pure_rf_multi.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/03_Models_and_Training/pure_rf_multi.py) — Production compiled pure-Python Random Forest model (8 features, 4 classes, 0 dependencies).
- `train_v2.py` & `pure_rf_v2.py` — Previous single-dataset model iterations (preserved for historical ablation study).
- `evaluate_model.py` — Standalone test harness for single-dataset evaluation.

### 4. `04_Dataset_Benchmarks/`
Benchmark data samples used for multi-year cross-validation:
- `csecicids2018_sample.csv` (13.5 MB) — Communications Security Establishment & CIC 2018 dataset.
- `cicddos2019_syn_sample.csv` (15.7 MB) — CIC DDoS 2019 SYN flood benchmark.
- `ciciot2023_sample.parquet` (13.4 MB) — High-density IoT traffic sample from CIC-IoT-2023.

### 5. `05_Gateway_Runtime/`
Production runtime software running on the Raspberry Pi edge device:
- [`dashboard.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/dashboard.py) — Live edge gateway engine featuring a real-time terminal UI (curses), socket sniffer, and telemetry logger.
- `pure_rf_multi.py` — Deployed inference engine on the Pi.
- `gateway.service` — Linux `systemd` daemon configuration for autonomous boot.
- `setup_systemd.sh` — Deployment script to enable and activate `gateway.service`.
- `check_pi_status.py` — Diagnostic script checking Pi reachability, systemd status, and resource usage.
- `deploy_remote.py` / `deploy_to_pi.ps1` — Automated SSH synchronization scripts.

### 6. `06_Testing_and_Telemetry/`
Edge stress testing, traffic generation, and telemetry analysis:
- [`plot_stress_test.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/06_Testing_and_Telemetry/plot_stress_test.py) — Matplotlib script generating time-series resource graphs from Pi telemetry.
- `stress_test_log.csv` — Live log data collected every 5 minutes on the Raspberry Pi.
- `stress_test_cpu_ram.png` — Visual evidence showing stable CPU (0.0–0.3%) and flat RAM (10.1%).
- `stress_test_latency_flows.png` — Visual evidence showing microsecond latency and flow counters.
- `simulate_traffic.py` — Synthetic traffic generator for edge load and attack simulation.

### 7. `07_Transcripts_and_History/`
Full chronological audit trail and media assets:
- `FULL_CHAT_TRANSCRIPT.md` — Complete chronological transcript of all development sessions.
- `transcript_full.jsonl` — Raw machine-readable session log.
- `chat_attachments/` — 56 historical screenshots, supervisor messages, and diagrams.

---

## ⚡ Quick Start & Verification Commands

### 1. Check Raspberry Pi Edge Gateway Status
```powershell
python 05_Gateway_Runtime/check_pi_status.py
```

### 2. Retrain Multi-Dataset Model & Export Pure-Python Code
```powershell
python 03_Models_and_Training/train_multi_dataset.py
```

### 3. Generate Stress Test Graphs from Pi Logs
```powershell
python 06_Testing_and_Telemetry/plot_stress_test.py
```

### 4. Deploy Updated Code to Raspberry Pi
```powershell
python 05_Gateway_Runtime/deploy_remote.py
```

---

## 🎓 Academic Defense Highlights (Viva Cheat Sheet)

1. **Why Pure-Python (`m2cgen`) instead of TensorFlow Lite / PyTorch?**
   - Eliminates 500MB+ heavyweight C/C++ dependencies and shared library version lock-in.
   - Runs out-of-the-box on standard Python 3.9+ with 24 MB RAM overhead.
   - Inference takes only $0.021\text{ ms}$ per packet flow.

2. **How did you overcome single-dataset testbed bias?**
   - We proved that a model trained strictly on CIC-IDS-2017 drops to **22.64% accuracy** on CSE-CIC-IDS-2018 due to domain shift.
   - By training across a joint 2017/2018/2019 feature space and validating on `CIC-IoT-2023`, the unified model maintains **96.70%** (multi-year) and **97.18%** (IoT) accuracy.

3. **How does the system ensure 24/7 reliability?**
   - Configured as an unprivileged/root `systemd` background service (`gateway.service`) with `Restart=always`.
   - Boots automatically upon power-on without requiring monitor, keyboard, or user login.
