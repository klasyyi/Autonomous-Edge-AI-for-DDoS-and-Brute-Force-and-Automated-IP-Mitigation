# Project File Audit & System Architecture
## Autonomous Edge-AI for DDoS and Brute-Force Detection with Automated IP Mitigation

> **Written in Simple Technical English**  
> **Target Audience:** Project Supervisor, Internal & External Examiners, and Project Reviewers  
> **Project Scope:** Autonomous, lightweight Network Intrusion Detection System (NIDS) deployed on a Raspberry Pi 4 edge gateway.

---

## 1. Executive Summary

This project develops an autonomous Edge-AI security gateway. It protects Internet of Things (IoT) and Local Area Network (LAN) devices against Distributed Denial of Service (DDoS) and SSH Brute-Force attacks. 

Unlike traditional security systems that send data to cloud servers or rely on heavy deep learning libraries, this system:
1. **Sniffs live network packets** directly on physical network interfaces (`eth0`/`wlan0`).
2. **Extracts 8 statistical flow features** in real time using an in-memory sliding window.
3. **Classifies threats in 0.021 milliseconds** using a pure-Python Random Forest model ($0$ external library dependencies).
4. **Mitigates attacks automatically** by adding Linux kernel `iptables` rules to drop attacker traffic immediately.
5. **Starts automatically on power-on** as an unattended Linux `systemd` background service.

---

## 2. Complete File-by-File Technical Audit

### 📁 Root Directory Files

| File | Type | Purpose in Simple Technical English |
| :--- | :--- | :--- |
| [`README.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/README.md) | Markdown | **Master Documentation Hub.** Explains project objectives, accuracy metrics across 4 datasets, hardware resource utilization, directory layout, and quickstart commands. |
| [`sync_to_onedrive.ps1`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/sync_to_onedrive.ps1) | PowerShell Script | **Automated OneDrive Backup Utility.** Uses Robocopy to synchronize all code, datasets, and reports to `OneDrive\Desktop\Final_Year_Final_Sem\FYP_Project` with zero data loss. |
| [`.gitignore`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/.gitignore) | Git Config | **Repository Filter.** Excludes temporary Python cache (`__pycache__`) and local editor files while retaining all project documentation, code, and datasets. |

---

### 📁 `01_Documentation_and_Viva/` (Academic Reports & Defense Guides)

| File | Format | Technical Audit & Function |
| :--- | :--- | :--- |
| [`PROJECT_FILE_AUDIT.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/PROJECT_FILE_AUDIT.md) | Markdown | **This Document.** Exhaustive, plain-English technical audit of every component, dataset, model, and script across the entire project. |
| [`KEY_LEARNINGS_AND_OVERCOMING_CHALLENGES.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/KEY_LEARNINGS_AND_OVERCOMING_CHALLENGES.md) | Markdown | **Engineering Narrative.** Documents the 7 hardest technical problems solved: overcoming single-dataset collapse ($22.64\% \rightarrow 96.70\%$), TinyML tree compilation, raw socket sniffing, and systemd daemonization. |
| [`FYP_EXECUTIVE_SUMMARY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/FYP_EXECUTIVE_SUMMARY.md) | Markdown | **One-Page Brief.** High-level overview of system design, performance figures, and thesis milestones for quick supervisor briefing. |
| [`MULTI_DATASET_EVALUATION.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/MULTI_DATASET_EVALUATION.md) | Markdown | **Cross-Dataset Benchmark Proof.** Details the resolution of testbed overfitting by training across 2017, 2018, and 2019 datasets and evaluating on the 105-device `CIC-IoT-2023` testbed. |
| [`LITERATURE_COMPARISON_ACCURACY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/LITERATURE_COMPARISON_ACCURACY.md) | Markdown | **Peer-Reviewed Benchmark Table.** Compares our $96.70\%$ multi-dataset and $97.18\%$ IoT accuracy scores against published papers from IEEE, Elsevier, and Frontiers. |
| [`LITERATURE_COMPARISON_EFFICIENCY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/LITERATURE_COMPARISON_EFFICIENCY.md) | Markdown | **Hardware Efficiency Benchmarking.** Compares our $24\text{ MB}$ pure-Python solution against Jetson Nano, Google Coral TPU, and standard deep learning frameworks. |
| [`EVALUATION_METHODOLOGY.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/EVALUATION_METHODOLOGY.md) | Markdown | **Mathematical Formulations.** Defines Precision, Recall, F1-Score, Confusion Matrices, and data leakage prevention protocols used during model evaluation. |
| [`VIVA_Results_and_Notes.md`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/01_Documentation_and_Viva/VIVA_Results_and_Notes.md) | Markdown | **Examiner Q&A Prep.** Direct answers to common viva questions regarding class imbalance, feature reduction, latency trade-offs, and edge deployment. |
| `multi_dataset_evaluation_report.txt` | Text | **Raw Model Classification Output.** Stratified classification report across $23,062$ unseen flows showing individual Precision, Recall, and F1 scores per attack class. |
| `Model_Evolution_and_Accuracy.txt` | Text | **Historical Model Progression Log.** Tracks the accuracy improvements from initial baseline prototypes to the final universal multi-dataset model. |
| `Findings_and_Tradeoffs.txt` | Text | **Engineering Trade-off Records.** Analyzes memory limits, packet queue sizing, sliding-window flow expiry, and CPU usage. |
| `evaluation_output.txt` | Text | **Single-Dataset Baseline Report.** Historical record of initial $99.98\%$ evaluation on CIC-IDS-2017 data before multi-dataset harmonization. |

---

### 📁 `02_Publications_Proof/` (Peer-Reviewed Academic Proof Papers)

This folder contains 12 verified PDF publications downloaded to back up every design decision and benchmark claim during the thesis defense:

1. `Sharafaldin2018_CICIDS2017.pdf` — Original paper introducing `CIC-IDS-2017` (ICISSP).
2. `Zhou2019_CICIDS2017_Ensemble.pdf` — Research validating tree-based ensembles on network traffic (Springer).
3. `Karim2020_CSE_CIC_IDS2018_Features.pdf` — Research identifying the optimal feature subset for `CSE-CIC-IDS-2018`.
4. `Almutairi2021_CICDDoS2019_IoT_ML.pdf` — Research on machine learning detection of DDoS attacks on IoT devices using `CIC-DDoS-2019`.
5. `Awotunde2024_CICIoT2023_Lightweight_ML.pdf` — Lightweight zero-trust intrusion detection evaluated on `CIC-IoT-2023`.
6. `Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf` — Study on resource-aware tree models and XAI on `CIC-IoT-2023`.
7. `Ali2025_IEEE_IoT_Edge_IDS.pdf` — IEEE IoT Journal benchmark on edge intrusion detection.
8. `Amuthadevi2024_TinyML_IoT_IDS.pdf` — Elsevier paper on TinyML intrusion detection for energy-constrained IoT.
9. `Hafid2024_IEEE_IoT_Edge_IDS.pdf` — IEEE benchmark on edge security gateway architectures.
10. `Mohale2024_Frontiers_XAI_IDS.pdf` — Frontiers in Computer Science benchmark on explainable AI in IDS.
11. `Cherukuri2024_Edge_vs_Cloud_AI.pdf` — Analysis comparing edge versus cloud AI computing overhead.
12. `Ibrahim2026_IoT_ML_NIDS.pdf` — Emerging machine learning NIDS architectures for IoT edge gateways.

---

### 📁 `03_Models_and_Training/` (Machine Learning Pipelines & Models)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`train_multi_dataset.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/03_Models_and_Training/train_multi_dataset.py) | Training Pipeline | Loads 2017, 2018, and 2019 datasets, harmonizes feature schemas, balances training data with SMOTE, trains a 25-tree Random Forest, and exports pure Python code via `m2cgen`. |
| [`pure_rf_multi.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/03_Models_and_Training/pure_rf_multi.py) | Compiled Model | 1.05 MB standalone Python code. Contains pure mathematical `if-else` decision trees. Evaluates an 8-feature vector and outputs class probabilities in $0.021\text{ ms}$ with **$0$ external dependencies**. |
| `train_v2.py` | Historical Training | Previous iteration training pipeline trained solely on 2017 traffic (preserved for ablation study). |
| `pure_rf_v2.py` | Historical Model | Previous 3-class compiled model based on single-dataset training. |
| `evaluate_model.py` | Evaluation Script | Standalone evaluation testbed calculating stratified metrics and classification reports. |

---

### 📁 `04_Dataset_Benchmarks/` (Cleaned Benchmark Data Samples)

| File | Size | Role in Simple Technical English |
| :--- | :--- | :--- |
| `csecicids2018_sample.csv` | 13.5 MB | Cleaned sample of Communications Security Establishment & CIC 2018 traffic (contains benign, DoS, and brute-force sessions). |
| `cicddos2019_syn_sample.csv` | 15.7 MB | Cleaned sample of modern reflective and volumetric SYN floods from CIC-DDoS-2019. |
| `ciciot2023_sample.parquet` | 13.4 MB | High-density flow samples collected from 105 physical IoT devices in the `CIC-IoT-2023` testbed. |

---

### 📁 `05_Gateway_Runtime/` (Production Edge Gateway Software)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`dashboard.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/dashboard.py) | Core Gateway Engine | Runs on the Raspberry Pi. Sniffs raw network packets asynchronously, maintains active flow tables in RAM, invokes `pure_rf_multi.py` every 5 packets, drops offending IPs via `iptables`, logs telemetry, and renders the terminal UI. |
| `pure_rf_multi.py` | Edge Runtime Model | Exact copy of the compiled 1.05 MB model stored in the runtime directory for clean local imports. |
| [`gateway.service`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/gateway.service) | Linux Daemon Config | `systemd` unit configuration file. Enables headless auto-boot on device startup with `Restart=always` and logging directed to `journalctl`. |
| [`setup_systemd.sh`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/setup_systemd.sh) | Service Installer | Shell script that installs `gateway.service` into `/etc/systemd/system/`, reloads the systemd daemon, and starts the service. |
| [`check_pi_status.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/check_pi_status.py) | Remote Health Monitor | Connects to the Raspberry Pi over SSH (`192.168.137.2`), checks if `gateway.service` is active, displays system uptime, RAM usage, active `iptables` drop rules, and reads recent telemetry logs. |
| [`deploy_remote.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/deploy_remote.py) | SSH Deployment Script | Transfers all updated runtime files from the host laptop to the Raspberry Pi via SFTP and triggers systemd restarts automatically. |
| [`deploy_to_pi.ps1`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/05_Gateway_Runtime/deploy_to_pi.ps1) | PowerShell Deployer | Alternative one-click Windows deployment script using SCP to transfer files to the Pi. |

---

### 📁 `06_Testing_and_Telemetry/` (Validation & Hardware Telemetry)

| File | Technical Role | Operation in Simple Technical English |
| :--- | :--- | :--- |
| [`plot_stress_test.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/06_Testing_and_Telemetry/plot_stress_test.py) | Graph Generator | Reads `stress_test_log.csv` and uses Matplotlib to generate two publication-ready figures: CPU/RAM over time and cumulative flows/latency over time. |
| `stress_test_log.csv` | Empirical Telemetry | Real-world continuous telemetry log recorded on the Raspberry Pi 4 every 5 minutes. Records timestamp, uptime, CPU%, RAM%, packets sniffed, benign/anomalous flows, active RAM flows, and average latency. |
| `stress_test_cpu_ram.png` | Output Chart | Visual graph proving CPU stability ($0.0\% - 0.3\%$) and flatline RAM ($10.1\% - 11.6\%$) over hours of operation with zero memory leaks. |
| `stress_test_latency_flows.png` | Output Chart | Visual graph showing cumulative flows processed, threat counts, and sub-millisecond inference latency ($<0.1\text{ ms}$). |
| [`simulate_traffic.py`](file:///c:/Users/syara/.gemini/antigravity/scratch/FYP/06_Testing_and_Telemetry/simulate_traffic.py) | Traffic Generator | Generates synthetic network traffic from the laptop to the Pi, including normal HTTP connections, rapid SYN bursts, and SSH connection probes. |

---

### 📁 `07_Transcripts_and_History/` (Project History & Audit Trail)

| File | Contents |
| :--- | :--- |
| `FULL_CHAT_TRANSCRIPT.md` | Complete chronological record of discussions, technical decisions, and milestones across all FYP development sessions. |
| `transcript_full.jsonl` | Machine-readable JSONL audit log of all development operations. |
| `chat_attachments/` | Directory containing 56 original supervisor screenshots, guidance diagrams, and reference papers preserved for thesis defense evidence. |

---

## 3. Code Sanitization & Comment Audit

Per project requirements, all code files were audited and sanitized:
1. **Removed Boilerplate & Noisy Comments:** Eliminated temporary `# Step 1`, `# Task 2`, and redundant explanatory comments.
2. **Self-Documenting Code:** Code structure, functions, and variable names are descriptive, readable, and written in Simple Technical English.
3. **No Heavy Runtime Dependencies:** The gateway software on the edge device relies solely on standard Python libraries (`scapy`, `psutil`, `rich`, and standard library modules). Machine learning inference requires **no** external C-libraries or frameworks.
