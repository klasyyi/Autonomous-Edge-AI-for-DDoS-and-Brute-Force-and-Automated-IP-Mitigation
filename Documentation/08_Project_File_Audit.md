# Project File Audit and System Architecture
## Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation

> **Author:** Final Year Project Student (Computer Science / Cyber Security)  
> **Target Audience:** Project Supervisor, Internal and External Examiners, and Project Reviewers  
> **Project Scope:** Autonomous, lightweight Network Intrusion Detection System (NIDS) deployed on a Raspberry Pi 4 edge gateway.

---

## 1. Executive Summary

In this project, I designed and built an autonomous Edge-AI security gateway to protect Internet of Things (IoT) and Local Area Network (LAN) devices against Distributed Denial of Service (DDoS) and SSH Brute-Force attacks.

Unlike conventional intrusion detection systems that offload packet captures to cloud servers or depend on resource-heavy deep learning libraries, my solution:
1. **Sniffs live network packets** directly on physical network interfaces (`eth0`/`wlan0`) using asynchronous raw sockets.
2. **Extracts 8 statistical flow features** in real time using an in-memory sliding-window table.
3. **Classifies threats in 0.021 milliseconds** using a pure-Python Random Forest decision tree model with zero external library dependencies.
4. **Mitigates attacks autonomously** by executing Linux kernel `iptables` rules to drop malicious traffic immediately.
5. **Starts automatically upon device boot** as an unattended Linux `systemd` background service.

---

## 2. Complete File-by-File Technical Audit

### Root Directory Files

| File | Type | Purpose in Simple Technical English |
| :--- | :--- | :--- |
| [`README.md`](../README.md) | Markdown | **Master Documentation Hub.** Explains my project objectives, multi-dataset accuracy benchmarks, hardware resource metrics, directory structure, and quickstart commands. |
| [`.gitignore`](../.gitignore) | Git Config | **Repository Filter.** Excludes temporary Python cache (`__pycache__`), local agent instructions (`AGENTS.md`), and local sync utilities (`sync_to_onedrive.ps1`) from public Git tracking. |

---

### Documentation/ (Academic Reports and Defense Guides)

The `Documentation` folder is organized with active, high-priority publications at the top, followed by labeled historical logs in the `history/` subfolder:

| File | Format | Technical Audit and Function |
| :--- | :--- | :--- |
| [`01_Executive_Summary.md`](01_Executive_Summary.md) | Markdown | **One-Page Brief.** High-level overview of system design, performance benchmarks, and milestones for quick review. |
| [`02_Key_Learnings_and_Challenges.md`](02_Key_Learnings_and_Challenges.md) | Markdown | **Engineering Narrative.** Documents the 7 hardest technical problems I solved, including cross-dataset distribution collapse (from 22.64% to 96.70%), TinyML decision tree compilation, raw socket sniffing, and systemd daemonization. |
| [`03_Multi_Dataset_Evaluation.md`](03_Multi_Dataset_Evaluation.md) | Markdown | **Cross-Dataset Benchmark Proof.** Details how I resolved testbed overfitting by training across 2017, 2018, and 2019 datasets and validating against the 105-device `CIC-IoT-2023` benchmark. |
| [`04_Literature_Accuracy_Comparison.md`](04_Literature_Accuracy_Comparison.md) | Markdown | **Peer-Reviewed Benchmark Table.** Compares my 96.70% multi-dataset and 97.18% IoT accuracy scores against published research papers from IEEE, Elsevier, and Frontiers. |
| [`05_Literature_Efficiency_Comparison.md`](05_Literature_Efficiency_Comparison.md) | Markdown | **Hardware Efficiency Benchmarking.** Compares my 24 MB pure-Python solution against Jetson Nano, Google Coral Edge TPU, and standard deep learning frameworks. |
| [`06_Evaluation_Methodology.md`](06_Evaluation_Methodology.md) | Markdown | **Mathematical Formulations.** Defines Precision, Recall, F1-Score, Confusion Matrices, and the train-test isolation protocol I used to eliminate data leakage. |
| [`07_Viva_Defense_Notes.md`](07_Viva_Defense_Notes.md) | Markdown | **Defense Q&A Prep.** Direct answers to common examination questions regarding class imbalance, feature reduction, latency trade-offs, and edge deployment. |
| [`08_Project_File_Audit.md`](08_Project_File_Audit.md) | Markdown | **This Document.** Exhaustive, plain-English technical audit of every component, dataset, model, and script across the entire repository. |

#### Documentation History Subfolder (`Documentation/history/`)
| File | Role |
| :--- | :--- |
| `history/history_multi_dataset_raw_report.txt` | Raw classification report across 23,062 unseen test flows showing individual Precision, Recall, and F1 scores per attack class. |
| `history/history_model_evolution_log.txt` | Tracks historical accuracy improvements from initial baseline prototypes to my final universal multi-dataset model. |
| `history/history_findings_and_tradeoffs.txt` | Engineering records analyzing memory limits, packet queue sizing, sliding-window flow expiry, and CPU usage. |
| `history/history_baseline_2017_evaluation.txt` | Historical record of initial 99.98% evaluation on CIC-IDS-2017 data before multi-dataset harmonization. |

---

### Publications/ (Peer-Reviewed Academic Proof Papers)

This folder contains 12 verified PDF publications that I collected to support every design decision and benchmark claim during project defense:

1. `Sharafaldin2018_CICIDS2017.pdf` — Original paper introducing `CIC-IDS-2017` (ICISSP).
2. `Zhou2019_CICIDS2017_Ensemble.pdf` — Research validating tree-based ensembles on network traffic (Springer).
3. `Karim2020_CSE_CIC_IDS2018_Features.pdf` — Research identifying the optimal feature subset for `CSE-CIC-IDS-2018`.
4. `Almutairi2021_CICDDoS2019_IoT_ML.pdf` — Research on machine learning detection of DDoS attacks on IoT devices using `CIC-DDoS-2019`.
5. `Awotunde2024_CICIoT2023_Lightweight_ML.pdf` — Lightweight zero-trust intrusion detection evaluated on `CIC-IoT-2023`.
6. `Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf` — Study on resource-aware tree models and XAI on `CIC-IoT-2023`.
7. `Ali2025_IEEE_IoT_Edge_IDS.pdf` — IEEE IoT Journal benchmark on edge intrusion detection.
8. `Amuthadevi2024_TinyML_IoT_IDS.pdf` — Elsevier paper on TinyML intrusion detection for energy-constrained IoT.
9. `Hafid2024_IEEE_IoT_Edge_IDS.pdf` — IEEE benchmark on edge security gateway architectures.
10. `Mohale2024_Frontiers_XAI_IDS.pdf` — Frontiers in Computer Science benchmark on explainable AI in intrusion detection.
11. `Cherukuri2024_Edge_vs_Cloud_AI.pdf` — Analysis comparing edge versus cloud AI computing overhead.
12. `Ibrahim2026_IoT_ML_NIDS.pdf` — Emerging machine learning NIDS architectures for IoT edge gateways.

---

### Models/ (Machine Learning Pipelines and Models)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`train_multi_dataset.py`](../Models/train_multi_dataset.py) | Active Training Pipeline | Loads 2017, 2018, and 2019 datasets, harmonizes feature schemas, balances training data with SMOTE, trains a 25-tree Random Forest, and exports pure Python code via `m2cgen`. |
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
| [`dashboard.py`](../Gateway/dashboard.py) | Core Gateway Engine | Runs on the Raspberry Pi. Sniffs raw network packets asynchronously, maintains active flow tables in RAM, invokes `pure_rf_multi.py` every 5 packets, drops offending IPs via `iptables`, logs telemetry, and renders the terminal UI. |
| `pure_rf_multi.py` | Edge Runtime Model | Exact copy of the compiled 1.05 MB model stored in the runtime directory for clean local imports. |
| [`gateway.service`](../Gateway/gateway.service) | Linux Daemon Config | `systemd` unit configuration file. Enables headless auto-boot on device startup with `Restart=always` and logging directed to `journalctl`. |
| [`setup_systemd.sh`](../Gateway/setup_systemd.sh) | Service Installer | Shell script that installs `gateway.service` into `/etc/systemd/system/`, reloads the systemd daemon, and starts the service. |
| [`check_pi_status.py`](../Gateway/check_pi_status.py) | Remote Health Monitor | Connects to the Raspberry Pi over SSH (`192.168.137.2`), checks if `gateway.service` is active, displays system uptime, RAM usage, active `iptables` drop rules, and reads recent telemetry logs. |
| [`deploy_remote.py`](../Gateway/deploy_remote.py) | SSH Deployment Script | Transfers updated runtime files from my host laptop to the Raspberry Pi via SFTP and triggers service restarts automatically. |
| [`deploy_to_pi.ps1`](../Gateway/deploy_to_pi.ps1) | PowerShell Deployer | Alternative one-click Windows deployment script using SCP to transfer files to the Pi. |

---

### Testing/ (Validation and Hardware Telemetry)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`plot_stress_test.py`](../Testing/plot_stress_test.py) | Graph Generator | Reads telemetry logs and uses Matplotlib to generate two publication-ready figures: CPU/RAM over time and cumulative flows/latency over time. |
| `stress_test_cpu_ram.png` | Output Chart | Visual graph proving CPU stability (0.0% to 0.3%) and flatline RAM (10.1% to 11.6%) over hours of operation with zero memory leaks. |
| `stress_test_latency_flows.png` | Output Chart | Visual graph showing cumulative flows processed, threat counts, and sub-millisecond inference latency (<0.1 ms). |
| [`simulate_traffic.py`](../Testing/simulate_traffic.py) | Traffic Generator | Generates synthetic network traffic from my laptop to the Pi, including normal HTTP connections, rapid SYN bursts, and SSH connection probes. |

#### Testing History Subfolder (`Testing/history/`)
| File | Role |
| :--- | :--- |
| `history/history_stress_test_log.csv` | Real-world continuous telemetry log recorded on the Raspberry Pi 4 every 5 minutes during testbed execution. |

---

### History/ (Project History and Reference Archive)

| File | Contents |
| :--- | :--- |
| `FULL_CHAT_TRANSCRIPT.md` | Chronological development records, technical discussions, and milestones across all FYP phases. |
| `transcript_full.jsonl` | Machine-readable audit file. |
| `chat_attachments/` | Directory containing 56 original reference screenshots, supervisor notes, and architecture diagrams. |

---

## 3. Code Sanitization and Comment Audit

I audited and sanitized all code files in the repository:
1. **Removed Boilerplate Comments:** Cleaned out temporary notes, numbered step headers, and redundant inline comments.
2. **Self-Documenting Code:** Functions, variables, and logic are explicitly named and structured to be self-explanatory.
3. **Zero Heavy Runtime Dependencies:** The gateway software on the edge device relies only on standard Python networking modules. Machine learning inference requires no external C-libraries or third-party ML frameworks.
