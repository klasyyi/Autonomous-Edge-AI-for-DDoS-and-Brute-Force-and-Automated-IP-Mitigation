# Project File Audit and System Architecture
## Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation
## 1. Executive Summary

In this project, I designed and built an autonomous Edge-AI security gateway to protect Internet of Things (IoT) and Local Area Network (LAN) devices against Distributed Denial of Service (DDoS) and SSH Brute-Force attacks.

Unlike conventional intrusion detection systems that offload packet captures to cloud servers or depend on resource-heavy deep learning libraries, my solution:
1. **Sniffs live network packets** directly on physical network interfaces (`eth0`/`br0`) using asynchronous raw sockets.
2. **Extracts 8 statistical flow features** in real time using an in-memory sliding-window table with time-to-live (TTL) eviction.
3. **Classifies threats in 0.021 milliseconds** (pure ML inference) and 0.08 to 0.17 milliseconds (end-to-end processing) using a pure-Python Random Forest decision tree model with zero external library dependencies.
4. **Mitigates attacks autonomously** by executing Linux kernel `iptables` rules to drop malicious traffic immediately (84.21 ms TTB for SYN floods; 62.07 ms TTB for SSH brute force), protected by safety whitelists, auto-unblock timers, and rule ceilings.
5. **Starts automatically upon device boot** as an unattended Linux `systemd` background service.

---

## 2. Complete File-by-File Technical Audit

### Root Directory Files

| File | Type | Purpose in Simple Technical English |
| :--- | :--- | :--- |
| [`README.md`](../README.md) | Markdown | **Master Documentation Hub.** Explains my project objectives, multi-dataset accuracy benchmarks, live physical mitigation metrics, hardware resource metrics, directory structure, and quickstart commands. |
| [`LICENSE`](../LICENSE) | Text | **Open-Source License.** Standard MIT License granting open academic and practical reuse of the codebase and architectures. |
| [`requirements.txt`](../requirements.txt) | Text | **Host Environment Dependencies.** Lists scikit-learn, pandas, imbalanced-learn, and m2cgen required strictly on the training workstation (the edge device requires zero external packages). |
| [`.gitignore`](../.gitignore) | Git Config | **Repository Filter.** Excludes temporary Python cache (`__pycache__`), local environment files, and operating system artifacts from public Git tracking. |

---

### Documentation/ (Academic Reports and Defense Guides)

The `Documentation` folder is organized with active, high-priority publications at the top, followed by labeled historical logs in the `history/` subfolder:

| File | Format | Technical Audit and Function |
| :--- | :--- | :--- |
| [`01_Executive_Summary.md`](01_Executive_Summary.md) | Markdown | **One-Page Brief.** High-level overview of system design, performance benchmarks, and milestones for quick review. |
| [`02_Key_Learnings_and_Challenges.md`](02_Key_Learnings_and_Challenges.md) | Markdown | **Engineering Narrative.** Documents the 7 hardest technical problems I solved, including cross-dataset distribution collapse (from 22.64% to 96.70%), TinyML decision tree compilation, raw socket sniffing, and systemd daemonization. |
| [`03_Multi_Dataset_Evaluation.md`](03_Multi_Dataset_Evaluation.md) | Markdown | **Cross-Dataset Benchmark Proof.** Details how I analyzed and reduced testbed overfitting by training across 2017, 2018, and 2019 datasets, evaluating Leave-One-Dataset-Out (LODO) domain collapse, and validating against the 105-device `CIC-IoT-2023` benchmark. |
| [`04_Literature_Accuracy_Comparison.md`](04_Literature_Accuracy_Comparison.md) | Markdown | **Peer-Reviewed Benchmark Table.** Compares my 96.70% multi-dataset and 97.18% IoT accuracy scores against published research papers from IEEE, Elsevier, and Frontiers, with explicit context on differing feature sets and test protocols. |
| [`05_Literature_Efficiency_Comparison.md`](05_Literature_Efficiency_Comparison.md) | Markdown | **Hardware Efficiency Benchmarking.** Compares my ~24.4 MB pure-Python solution against Jetson Nano, Google Coral Edge TPU, and standard deep learning frameworks, clarifying single-board computer versus microcontroller distinctions. |
| [`06_Evaluation_Methodology.md`](06_Evaluation_Methodology.md) | Markdown | **Mathematical Formulations.** Defines Precision, Recall, F1-Score, Confusion Matrices, baseline classifier comparisons (Heuristics, Logistic Regression, Decision Trees), data leakage isolation protocols, and live physical closed-loop hardware mitigation results. |
| [`07_Viva_Defense_Notes.md`](07_Viva_Defense_Notes.md) | Markdown | **Defense Q&A Prep.** Direct answers to common examination questions regarding why ML is necessary, anti-spoofing mitigation safeguards, LODO failure dynamics, longevity versus stress testing, and live Time-to-Block metrics. |
| [`08_Project_File_Audit.md`](08_Project_File_Audit.md) | Markdown | **This Document.** Exhaustive, plain-English technical audit of every component, dataset, model, and script across the entire repository. |

#### Documentation History Subfolder (`Documentation/history/`)
| File | Role |
| :--- | :--- |
| `history/history_multi_dataset_raw_report.txt` | Raw classification report across 23,062 unseen test flows showing individual Precision, Recall, and F1 scores per attack class. |
| `history/history_lodo_and_baselines.txt` | Raw empirical logs of Leave-One-Dataset-Out cross-validation collapse across 2017/2018/2019 and comparison against baseline classifiers. |
| `history/history_live_mitigation_benchmark.txt` | Raw empirical measurements of live physical attack mitigation on the Raspberry Pi 4 (100% detection rate, 0.0% FPR, 84.21 ms SYN flood TTB, 62.07 ms SSH brute force TTB). |
| `history/history_model_evolution_log.txt` | Tracks historical accuracy improvements from initial baseline prototypes to my final universal multi-dataset model. |
| `history/history_findings_and_tradeoffs.txt` | Engineering records analyzing memory limits, packet queue sizing, sliding-window flow expiry, and CPU usage. |
| `history/history_baseline_2017_evaluation.txt` | Historical record of initial 99.98% evaluation on CIC-IDS-2017 data before multi-dataset harmonization. |

---

### Publications/ (Peer-Reviewed Academic Proof Papers)

This folder contains 12 verified PDF publications and a formal bibliography that I collected to support every design decision and benchmark claim during project defense:

- [`REFERENCES.md`](../Publications/REFERENCES.md) — Comprehensive academic bibliography containing complete bibliographic metadata, DOIs, publication venues, and BibTeX citations for all 12 referenced papers.
- `Sharafaldin2018_CICIDS2017.pdf` — Original paper introducing `CIC-IDS-2017` (ICISSP).
- `Zhou2019_CICIDS2017_Ensemble.pdf` — Research validating tree-based ensembles on network traffic (Springer).
- `Karim2020_CSE_CIC_IDS2018_Features.pdf` — Research identifying the optimal feature subset for `CSE-CIC-IDS-2018`.
- `Almutairi2021_CICDDoS2019_IoT_ML.pdf` — Research on machine learning detection of DDoS attacks on IoT devices using `CIC-DDoS-2019`.
- `Awotunde2024_CICIoT2023_Lightweight_ML.pdf` — Lightweight zero-trust intrusion detection evaluated on `CIC-IoT-2023`.
- `Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf` — Study on resource-aware tree models and XAI on `CIC-IoT-2023`.
- `Ali2025_IEEE_IoT_Edge_IDS.pdf` — IEEE IoT Journal benchmark on edge intrusion detection.
- `Amuthadevi2024_TinyML_IoT_IDS.pdf` — Elsevier paper on TinyML intrusion detection for energy-constrained IoT.
- `Hafid2024_IEEE_IoT_Edge_IDS.pdf` — IEEE benchmark on edge security gateway architectures.
- `Mohale2024_Frontiers_XAI_IDS.pdf` — Frontiers in Computer Science benchmark on explainable AI in intrusion detection.
- `Cherukuri2024_Edge_vs_Cloud_AI.pdf` — Analysis comparing edge versus cloud AI computing overhead.
- `Ibrahim2026_IoT_ML_NIDS.pdf` — Emerging machine learning NIDS architectures for IoT edge gateways.

---

### Models/ (Machine Learning Pipelines and Models)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`train_multi_dataset.py`](../Models/train_multi_dataset.py) | Active Training Pipeline | Loads 2017, 2018, and 2019 datasets, harmonizes feature schemas, balances training data with SMOTE, trains a 25-tree Random Forest, and exports pure Python code via `m2cgen`. |
| [`evaluate_lodo_and_baselines.py`](../Models/evaluate_lodo_and_baselines.py) | LODO and Baseline Suite | Evaluates zero-shot domain collapse via Leave-One-Dataset-Out (LODO) cross-validation and benchmarks the proposed Random Forest against Heuristics, Logistic Regression, and shallow Decision Trees. |
| [`pure_rf_multi.py`](../Models/pure_rf_multi.py) | Active Compiled Model | 1.05 MB standalone Python code. Contains pure mathematical if-else decision trees. Evaluates an 8-feature vector and outputs class probabilities in 0.021 ms with **zero external dependencies**. |

#### Models History Subfolder (`Models/history/`)
| File | Role |
| :--- | :--- |
| `history/history_train_v2_single_dataset.py` | Previous iteration training pipeline trained solely on 2017 traffic (preserved for ablation study). |
| `history/history_pure_rf_v2_model.py` | Previous 3-class compiled model based on single-dataset training. |
| `history/history_evaluate_model.py` | Previous standalone evaluation testbed calculating single-dataset metrics. |

---

### Datasets/ (Cleaned Benchmark Data Samples)

| File | Size | Role in Simple Technical English |
| :--- | :--- | :--- |
| `csecicids2018_sample.csv` | 13.5 MB | Cleaned sample of CSE-CIC-IDS-2018 traffic (contains benign, DoS, and brute-force sessions). |
| `cicddos2019_syn_sample.csv` | 15.7 MB | Cleaned sample of modern reflective and volumetric SYN floods from CIC-DDoS-2019. |
| `ciciot2023_sample.parquet` | 13.4 MB | High-density flow samples collected from 105 physical IoT devices in the `CIC-IoT-2023` testbed. |

---

### Gateway/ (Production Edge Gateway Software)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`dashboard.py`](../Gateway/dashboard.py) | Core Gateway Engine | Runs on the Raspberry Pi. Sniffs raw network packets asynchronously, auto-detects active bridge (`br0`), maintains active flow tables in RAM with 60s TTL eviction, evaluates flows via `pure_rf_multi.py`, blocks malicious IPs via `iptables` (with permanent whitelist, 300s auto-unblock TTL, and 500-rule cap), logs telemetry, and renders the terminal UI. |
| `pure_rf_multi.py` | Edge Runtime Model | Exact copy of the compiled 1.05 MB model stored in the runtime directory for clean local imports. |
| [`gateway.service`](../Gateway/gateway.service) | Linux Daemon Config | `systemd` unit configuration file. Enables headless auto-boot on device startup with `Restart=always` and logging directed to `journalctl`. |
| [`setup_systemd.sh`](../Gateway/setup_systemd.sh) | Service Installer | Shell script that installs `gateway.service` into `/etc/systemd/system/`, reloads the systemd daemon, and starts the service. |
| [`check_pi_status.py`](../Gateway/check_pi_status.py) | Remote Health Monitor | Connects to the Raspberry Pi over SSH (`192.168.137.2`), checks if `gateway.service` is active, displays system uptime, RAM usage, active `iptables` drop rules, and reads recent telemetry logs using secure interactive credentials. |
| [`deploy_remote.py`](../Gateway/deploy_remote.py) | SSH Deployment Script | Transfers updated runtime files from my host laptop to the Raspberry Pi via SFTP and triggers service restarts automatically using secure interactive credentials. |
| [`deploy_to_pi.ps1`](../Gateway/deploy_to_pi.ps1) | PowerShell Deployer | Alternative one-click Windows deployment script using SCP to transfer files to the Pi. |

---

### Testing/ (Validation and Hardware Telemetry)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`stress_test_24h_runner.py`](../Testing/stress_test_24h_runner.py) | 24-Hour Diurnal Soak Runner | Executes the 24-hour diurnal reliability test over physical Ethernet. Manages 288 checkpoints, dispatches continuous benign traffic, triggers hourly attack pulses, queries remote Pi telemetry over SSH, logs 14 parameters, and inhibits Windows sleep. |
| [`plot_24h_stress.py`](../Testing/plot_24h_stress.py) | 24-Hour Telemetry Plotter | Reads `history_24h_stress_log.csv` and renders publication-grade time-series figures showing CPU %, RAM MB, SoC temperature, and physical Time-to-Block over the 24-hour cycle. |
| `stress_test_24h_telemetry.png` | Publication Chart | Visual evidence proving CPU stability (mean 25.61%), cool SoC temperature (mean 38.81 °C), and flatline RAM (83.54 MB RSS) across the full 24-hour soak test with zero memory leakage. |
| `stress_test_24h_mitigation.png` | Publication Chart | Visual evidence showing physical Time-to-Block (85.72 ms DDoS, 62.83 ms SSH) across 20 live attack pulses and 15,381 benign flows with 0.000% False Positive Rate. |
| [`bench_live_mitigation.py`](../Testing/bench_live_mitigation.py) | Live Mitigation Benchmark | Executes real-time physical closed-loop attack trials against the Raspberry Pi 4 across volumetric SYN floods and SSH brute force, capturing precise empirical Time-to-Block (TTB) and kernel rule confirmation. |
| [`plot_stress_test.py`](../Testing/plot_stress_test.py) | Graph Generator | Reads telemetry logs and uses Matplotlib to generate preliminary soak test figures. |
| `stress_test_cpu_ram.png` | Output Chart | Preliminary visual graph showing hardware resource stability. |
| `stress_test_latency_flows.png` | Output Chart | Preliminary visual graph showing cumulative flows processed. |
| [`simulate_traffic.py`](../Testing/simulate_traffic.py) | Traffic Generator & Stress Harness | Multi-threaded traffic generator and stress test harness supporting benign sessions, rapid SYN floods, and SSH brute-force probes. |

#### Testing History Subfolder (`Testing/history/`)
| File | Role |
| :--- | :--- |
| `history/history_24h_stress_log.csv` | Full 288-checkpoint empirical telemetry dataset recorded during the continuous 24-hour physical soak test. Contains 14 metrics captured every 5 minutes. |
| `history/history_stress_test_log.csv` | Preliminary telemetry log recorded on the Raspberry Pi 4 during early longevity testing. |

---

### tests/ (Automated Unit and Safety Regression Test Suite)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`test_model.py`](../tests/test_model.py) | ML Inference Test | Verifies zero external dependency imports, checks output probability vector structure, validates Benign, DDoS, and SSH-Patator classifications against ground-truth vectors, and enforces sub-0.1 ms latency constraints. |
| [`test_mitigation_safety.py`](../tests/test_mitigation_safety.py) | Anti-Spoofing Safety Test | Verifies permanent IP whitelist protection for core infrastructure, validates 300-second block TTL auto-unblock, enforces the 500-rule iptables cap, and tests 60-second sliding-window flow eviction. |
| [`test_flow_features.py`](../tests/test_flow_features.py) | Feature Extraction Test | Verifies real-time 8-feature mathematical extraction, standard deviation calculations, and safe division handling under zero-packet edge cases. |

---

## 3. Code Sanitization and Comment Audit

I audited and sanitized all code files in the repository:
1. **Removed Boilerplate Comments:** Cleaned out temporary notes, numbered step headers, and redundant inline comments.
2. **Self-Documenting Code:** Functions, variables, and logic are explicitly named and structured to be self-explanatory.
3. **Zero Heavy Runtime Dependencies:** The gateway software on the edge device relies only on standard Python networking modules. Machine learning inference requires no external C-libraries or third-party ML frameworks.
