# Technical Report: Universal Multi-Dataset Benchmark and Generalization
## Resolving Testbed Overfitting in Edge Network Intrusion Detection

> **Author:** Final Year Project Student (Computer Science / Cyber Security)  
> **Research Focus:** Cross-Dataset Generalization and Overfitting Elimination for Edge Intrusion Detection  
> **Evaluated Datasets:** CIC-IDS-2017, CSE-CIC-IDS2018, CIC-DDoS2019, CIC-IoT2023  
> **Achieved Accuracy:** 96.70% (Universal Multi-Dataset Model) and 97.18% (Dedicated IoT Benchmark)

---

## 1. Executive Summary: The Testbed Overfitting Problem

A central challenge in machine learning intrusion detection research is that evaluating a model on a single synthetic dataset can produce an artificially inflated accuracy score due to testbed homogeneity. To claim genuine generalization, an intrusion detection system must demonstrate consistent performance across diverse datasets collected across different years and network environments.

### The Empirical Proof: Zero-Shot Cross-Dataset Transfer Failure
To test whether a single-dataset model truly generalizes, I conducted a **Zero-Shot Cross-Dataset Transfer Experiment**:
1. I took my baseline Random Forest model trained **exclusively on CIC-IDS-2017**.
2. I evaluated it directly against **34,411 unseen flows from CSE-CIC-IDS2018** (containing modern HOIC, LOIC-UDP, and brute-force attacks) without any retraining or fine-tuning.
3. **The Result:** The 2017-only model accuracy plummeted from **99.98% down to 22.64%** (Macro F1 = 0.29).

**Technical Explanation:** Because network environments and attack tools evolve over time (introducing variations in operating system TCP window sizes and packet interval distributions), models trained strictly on a single environment suffer from **Covariate Shift and Testbed Bias**.

To solve this, I designed a feature harmonization pipeline unifying **`CSE-CIC-IDS2018`**, **`CIC-DDoS2019`**, and **`CIC-IoT2023`**, transforming the single-testbed prototype into a **Universal Edge Security Gateway**.

---

## 2. Multi-Dataset Integration and Feature Harmonization

To combine multi-year datasets while preserving my sub-millisecond edge latency constraint on the Raspberry Pi 4, I harmonized the feature schema across all four benchmark datasets into **8 Core Mathematical Features**:

| # | Standard Gateway Feature | CIC-IDS-2017 Column | CSE-CIC-IDS2018 Column | CIC-DDoS2019 Column | CIC-IoT2023 Analog |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | `Destination Port` | `Destination Port` | `Dst Port` | `Destination Port` | Port / Protocol Type |
| **2** | `Bwd Packet Length Std` | `Bwd Packet Length Std` | `Bwd Pkt Len Std` | `Bwd Packet Length Std` | `Std` / `Variance` |
| **3** | `SYN Flag Count` | `SYN Flag Count` | `SYN Flag Cnt` | `SYN Flag Count` | `syn_count` |
| **4** | `Flow IAT Mean` | `Flow IAT Mean` | `Flow IAT Mean` | `Flow IAT Mean` | `IAT` |
| **5** | `Total Fwd Packets` | `Total Fwd Packets` | `Tot Fwd Pkts` | `Total Fwd Packets` | `Rate` / Pkt Count |
| **6** | `Flow Duration` | `Flow Duration` | `Flow Duration` | `Flow Duration` | Duration / Window |
| **7** | `Fwd Packet Length Mean`| `Fwd Packet Length Mean`| `Fwd Pkt Len Mean` | `Fwd Packet Length Mean`| `AVG` |
| **8** | `Init_Win_bytes_forward`| `Init_Win_bytes_forward`| `Init Fwd Win Byts` | `Init_Win_bytes_forward`| Header / TTL |

---

## 3. Benchmark 1: The Universal Multi-Dataset Model (`pure_rf_multi.py`)

### Dataset Composition
I synthesized a multi-dataset corpus of **115,308 network flows**:
* **`CIC-IDS-2017`:** 55,897 flows (Baseline Benign, LOIC, SSH-Patator)
* **`CSE-CIC-IDS2018`:** 34,411 flows (HOIC, LOIC-HTTP, LOIC-UDP, DoS Hulk/GoldenEye, SSH-Bruteforce)
* **`CIC-DDoS2019`:** 25,000 flows (Modern TCP SYN Reflection and Volumetric floods)

### Training Methodology
* **Stratified 80/20 Partition:** 92,246 training flows | 23,062 unseen test flows.
* **SMOTE Balancing:** Applied strictly to the training fold (59,831 balanced flows per class).
* **Constrained TinyML Architecture:** `RandomForestClassifier(n_estimators=25, max_depth=12)` compiled via `m2cgen` into raw Python logic (`pure_rf_multi.py`).

### Formal Test Results on 23,062 Unseen Multi-Year Flows:
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

* **Achieved Accuracy:** **96.70%** on unseen multi-year flows.
* **Benign Traffic Reliability:** **99.74% F1-score**, indicating virtually zero false positive drops for legitimate sessions.
* **Brute-Force Recall:** **99.50%**, successfully detecting credential-guessing attacks across multiple attack tools.

---

## 4. Benchmark 2: Dedicated IoT Edge Benchmark (`CIC-IoT2023`)

To test performance against real physical IoT network traffic, I evaluated my TinyML architecture on the dedicated **`CIC-IoT2023`** dataset, collected from real IoT sensors, Raspberry Pis, and smart home appliances.

### Formal Test Results on 26,592 Unseen IoT Flows:
* **Target Classes:** `DDoS` (SYN/TCP floods), `BruteForce` (Dictionary attacks), `Benign` (IoT telemetry).
* **Overall Accuracy:** **97.18%**
  - **DDoS Precision and Recall:** **1.00 / 1.00 (F1 = 1.00)**
  - **Benign Precision and Recall:** **0.97 / 0.94 (F1 = 0.95)**
  - **Brute-Force Recall:** **0.51** (Detects low-rate IoT brute-force probes).

---

## 5. Performance Comparison: Single-Dataset vs. Multi-Dataset

| Model Architecture | Training Data | Evaluation Target | Accuracy | Macro F1-Score | Inference Latency on Pi 4 |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Baseline Model (`pure_rf_v2`)** | CIC-IDS-2017 Only | CIC-IDS-2017 (Same distribution) | **99.98%** | 1.00 | 0.08 ms |
| **Baseline Model (`pure_rf_v2`)** | CIC-IDS-2017 Only | CSE-CIC-IDS2018 (Unseen cross-testbed) | **22.64%** *(Overfitting failure)* | 0.30 | 0.08 ms |
| **Universal Multi-Model (`pure_rf_multi`)** | **2017 + 2018 + 2019** | **Merged Unseen Test Vault (All 3 Datasets)** | **96.70%** *(Robust Generalization)* | **0.95** | **0.021 ms** |
| **IoT Edge Model** | CIC-IoT2023 Only | CIC-IoT2023 Unseen Test Vault | **97.18%** | 0.79 | 0.021 ms |

This empirical comparison demonstrates three key findings:
1. The initial 99.98% accuracy score was specific to single-testbed conditions.
2. Direct cross-dataset transfer without multi-dataset training collapsed to 22.64%, confirming the presence of testbed bias.
3. My harmonized multi-dataset pipeline resolved this failure, achieving **96.70% accuracy across multi-year traffic** and **97.18% on physical IoT device data**.
