# Machine Learning Evaluation Methodology and Experimental Design

## 1. Overview and Research Objective

In this project, my objective was to design, train, evaluate, and deploy an autonomous Network Intrusion Detection System (NIDS) running on a physical **Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.5 GHz, 4GB RAM)**.

The classification engine identifies network traffic flows into three distinct behavioral classes:
1. **`BENIGN`**: Legitimate network sessions (HTTP/HTTPS web browsing, DNS queries, legitimate SSH administration).
2. **`DDoS`**: Volumetric and application-layer denial-of-service traffic (TCP SYN floods, UDP packet storms, HTTP GET floods).
3. **`SSH-Patator`**: Brute-force credential guessing probes directed against Port 22.

### The TinyML Edge Constraint
Deploying machine learning models directly onto embedded edge nodes introduces strict operational constraints:
- **Sub-Millisecond Latency:** Inference must execute in under 0.10 ms per flow to avoid packet backlog during traffic bursts.
- **Dependency Elimination:** Heavy runtime libraries (`scikit-learn`, `numpy`, `scipy`, `pandas`) must be eliminated from the edge environment to avoid runtime conflicts and multi-hundred-megabyte disk overhead.
- **Low Memory Footprint:** The classification process must operate within minimal system RAM (~24 MB) without inducing memory paging.

---

## 2. Experimental Evolution: Two-Phase Methodology

To ensure scientific validity, I conducted my research across two distinct phases:

### Phase 1: Baseline Single-Dataset Investigation and Discovery of Testbed Bias
In my initial experiments, I trained a 20-tree Random Forest classifier (`pure_rf_v2.py`) solely on the **CIC-IDS-2017** benchmark. While this model achieved **99.98% accuracy** and 0.08 ms latency when evaluated against a 20% holdout split of CIC-IDS-2017 (132,685 flows), evaluating it against unseen traffic from **CSE-CIC-IDS-2018** resulted in an immediate collapse to **22.64% accuracy**.

**Root Cause Analysis:** Single-dataset training caused the decision boundaries to overfit to static laboratory artifacts—such as fixed subnet IP ranges, synthetic inter-arrival time constants, and uniform background traffic—rather than learning invariant protocol signatures.

### Phase 2: Universal Multi-Dataset Harmonization and Physical IoT Validation
To eliminate testbed bias, I engineered a cross-dataset feature harmonization pipeline combining three benchmark years (**CIC-IDS-2017**, **CSE-CIC-IDS-2018**, and **CIC-DDoS-2019**), yielding a unified corpus of **115,308 network flows**. I then validated the resulting model against **26,592 flows from the physical 105-device `CIC-IoT-2023` testbed**, establishing true cross-dataset generalization.

---

## 3. Mathematical Formulations of Evaluation Metrics

To evaluate model performance objectively across balanced and imbalanced traffic conditions, I formulated the evaluation metrics as follows:

Let $TP$ denote True Positives, $FP$ False Positives, $TN$ True Negatives, and $FN$ False Negatives for a given class $c \in C$:

### 1. Classification Accuracy
$$\text{Accuracy} = \frac{\sum_{c \in C} TP_c}{\sum_{c \in C} (TP_c + FP_c + TN_c + FN_c)}$$

### 2. Precision
$$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c}$$
High precision in network security ensures legitimate user connections are not falsely flagged or blocked by `iptables`.

### 3. Recall (Detection Rate)
$$\text{Recall}_c = \frac{TP_c}{TP_c + FN_c}$$
High recall ensures malicious intrusions are detected reliably without evading perimeter defenses.

### 4. F1-Score (Harmonic Mean)
$$F_1 = 2 \times \frac{\text{Precision}_c \times \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

### 5. Macro-Averaged F1-Score
$$\text{Macro } F_1 = \frac{1}{|C|} \sum_{c \in C} F_{1, c}$$
Macro F1 assigns equal weight to all classes, ensuring minority attack categories (e.g., SSH-Patator) are evaluated with equal rigor to majority Benign traffic.

---

## 4. Feature Selection and Harmonization (The 8 Core Features)

Rather than evaluating all 80+ features from raw PCAP captures—which causes severe CPU caching delays on ARM hardware—I analyzed feature importance across all three datasets and distilled the flow vector down to **8 core mathematical features**:

| # | Harmonized Feature Name | Data Type | Units | Physical Network Rationale |
| :-: | :--- | :---: | :---: | :--- |
| **1** | `Destination Port` | Integer | - | Discriminates service targets (Port 22 for SSH brute-force, Port 80/443 for web DDoS, ephemeral ports). |
| **2** | `Bwd Packet Length Std` | Float | Bytes | Standard deviation of response payload sizes. In volumetric floods, the victim rarely responds, driving this value toward 0. |
| **3** | `SYN Flag Count` | Integer | - | Counts synchronization handshake packets; volumetric SYN floods exhibit abnormally high ratios relative to ACK packets. |
| **4** | `Flow IAT Mean` | Float | $\mu s$ | Mean packet Inter-Arrival Time within the flow. Automated attack scripts transmit at rapid intervals (< 1000 $\mu s$), whereas human activity exhibits variable pauses. |
| **5** | `Total Fwd Packets` | Integer | - | Cumulative count of outbound packets transmitted by the source IP. |
| **6** | `Flow Duration` | Float | $\mu s$ | Total lifetime of the bidirectional TCP session. |
| **7** | `Fwd Packet Length Mean` | Float | Bytes | Average payload size of client packets. Brute-force probes send small, repetitive authentication strings. |
| **8** | `Init_Win_bytes_forward` | Integer | Bytes | Size of initial TCP window advertisement, acting as an OS/client network stack fingerprint. |

---

## 5. Data Leakage Prevention and Class Balancing (SMOTE)

### Strict Train/Test Separation Protocol
A frequent methodological flaw in published literature is applying data normalization or oversampling across the entire dataset prior to partitioning. This bleeds statistical patterns and synthetic test samples into the training set, producing invalid accuracy claims.

To eliminate data leakage, I enforced a strict protocol:
1. **Pre-Split Partitioning:** The complete harmonized dataset (115,308 flows) was stratified into an **80% training set (92,246 flows)** and a **20% unseen test vault (23,062 flows)** using a locked seed (`random_state = 42`).
2. **Strict Training-Fold Oversampling:** The Synthetic Minority Over-sampling Technique (SMOTE) was executed **exclusively on the 80% training fold**:
   $$x_{\text{new}} = x_i + \lambda \times (x_{zi} - x_i), \quad \lambda \sim U(0, 1)$$
   This balanced the minority classes (`DDoS` and `SSH-Patator`) up to 59,831 samples each within the training partition.
3. **Pristine Test Vault:** The 20% test fold remained 100% untouched, consisting solely of natural, unaugmented network traffic.

---

## 6. Model Architecture and TinyML Compilation

### Hyperparameter Bounds
I trained a constrained `RandomForestClassifier` with the following bounded parameters:
- `n_estimators = 25`: Selected to provide sufficient ensemble variance reduction while keeping the compiled file size to 1.05 MB.
- `max_depth = 12`: Constrained to prevent individual tree branches from memorizing specific host IP addresses or transient timestamps.
- `criterion = 'gini'`: Gini impurity metric for splitting criteria.

### Compilation to Pure Python (`pure_rf_multi.py`)
Using `m2cgen`, I cross-compiled the trained ensemble into pure Python branching code:
- Converts all 25 decision trees into deterministic nested `if/else` statements.
- **Zero Runtime Dependencies:** Requires bare Python 3 with no imports of `numpy`, `scipy`, or `scikit-learn` on the edge gateway.
- **Compiled File Size:** Exactly **1.05 MB**.
- **Inference Latency:** **0.021 ms per flow** (~47,600 classifications per second).
- **RAM Footprint:** **~24 MB RAM** (only 10.1% to 11.6% of system memory on the Raspberry Pi 4).

---

## 7. Formal Experimental Evaluation Results

### A. Universal Multi-Dataset Evaluation (23,062 Unseen Flows)
Evaluated across unseen test flows spanning CIC-IDS-2017, CSE-CIC-IDS-2018, and CIC-DDoS-2019:

| Traffic Class | Precision | Recall | F1-Score | Support (Flows) |
| :--- | :---: | :---: | :---: | :---: |
| **BENIGN** | 0.9975 | 0.9973 | 0.9974 | 5,282 |
| **DDoS** | 0.9987 | 0.9511 | 0.9743 | 14,958 |
| **SSH-Patator** | 0.7941 | 0.9950 | 0.8833 | 2,822 |
| **Overall Accuracy** | - | - | **0.9670 (96.70%)** | **23,062** |
| **Macro Average** | **0.9301** | **0.9812** | **0.9517** | **23,062** |
| **Weighted Average** | **0.9734** | **0.9670** | **0.9685** | **23,062** |

- **Multi-Dataset Accuracy:** **96.70%** across multi-year unseen network traffic.
- **Benign Traffic Reliability:** **99.74% F1-score**, ensuring legitimate traffic is preserved without false drops.
- **Brute-Force Recall:** **99.50%**, ensuring credential-guessing attacks are captured reliably.

### B. Dedicated Physical IoT Testbed Evaluation (`CIC-IoT-2023`)
Evaluated on **26,592 unseen flows** collected from 105 physical smart home and edge devices:
- **Overall IoT Accuracy:** **97.18%**
- **DDoS Precision / Recall / F1:** **1.00 / 1.00 / 1.00**
- **Benign Precision / Recall / F1:** **0.97 / 0.94 / 0.95**

### C. Summary Performance Across Model Iterations

| Metric / Parameter | Phase 1 Baseline (`pure_rf_v2`) | Phase 2 Multi-Dataset (`pure_rf_multi`) | Physical IoT Benchmark |
| :--- | :---: | :---: | :---: |
| **Training Corpus** | CIC-IDS-2017 Only | 2017 + 2018 + 2019 Unified | CIC-IoT-2023 Testbed |
| **Overall Accuracy** | 99.98% (2017) / 22.64% (2018 transfer) | **96.70%** (Robust Generalization) | **97.18%** |
| **Macro F1-Score** | 1.00 (same-domain) / 0.29 (cross-domain) | **0.9517** | 0.79 / 0.96 (per-class) |
| **Inference Latency** | 0.080 ms / flow | **0.021 ms / flow** | **0.021 ms / flow** |
| **Compiled Model Size** | 0.84 MB | **1.05 MB** | **1.05 MB** |
| **Edge RAM Footprint** | ~24 MB | **~24 MB** | **~24 MB** |
| **External Dependencies** | None (Pure Python) | **None (Pure Python)** | **None (Pure Python)** |

---

## 8. Empirical Hardware Evaluation Protocol: Longevity Soak vs. Volumetric Stress Testing

To establish empirical rigor, I separated hardware evaluation into two distinct testing protocols:

### A. Extended Hardware Longevity & Memory Stability Soak Test
* **Objective:** Validate daemon persistence, memory stability, and heap isolation over multi-hour headless operation.
* **Execution:** Continuous physical hardware execution on the Raspberry Pi 4 under ambient local traffic (~1 pkt/sec) recorded at 5-minute telemetry intervals (`history_stress_test_log.csv`).
* **Verified Findings:**
  - **Memory Stability:** RAM consumption remained strictly flat between **10.1% and 11.6%** over ~2.5 hours, confirming zero memory leaks.
  - **Idle Processor Draw:** CPU load stayed between **0.0% and 0.3%**, showing minimal baseline background footprint.
  - **Memory Bounding:** Protected by in-memory sliding-window TTL eviction (60-second inactivity prune).

### B. Active Volumetric Attack Stress Test
* **Objective:** Stress network buffers, measure packet handling thresholds, and quantify autonomous mitigation speed under attack.
* **Execution:** Multi-threaded synthetic flood generation using `simulate_traffic.py --mode stress` (1,000+ packets/sec bursts across randomized ports).
* **Measured Latency Disaggregation:**
  1. **Pure Machine Learning Inference Latency:** **0.021 ms** (pure-Python decision tree execution via `m2cgen`).
  2. **End-to-End Ingestion-to-Mitigation Latency:** **0.08 ms to 0.17 ms** (including raw packet capture, 5-tuple table update, and Linux kernel `iptables` drop rule execution).

---

## 9. Threats to Validity and System Operating Envelope

In accordance with scientific best practices, I identified the operational envelope and boundary conditions of the system:
1. **Transport Protocol Focus:** The current feature extraction pipeline monitors TCP session behaviors. Volumetric UDP amplification or ICMP ping storms are delegated to kernel-level SYN cookies and hardware firewalling.
2. **Asymmetric Routing Sensitivity:** The feature vector incorporates backward packet statistics (`Bwd Packet Length Std`). In networks with asymmetric routing paths, flows without return traffic are supplemented by Tier 1 Source-IP rate tracking.
3. **Port-Independent Behavioral Detection:** To prevent attackers from evading detection on non-standard ports (e.g., SSH bound to port 2222), the model couples destination port with inter-arrival time and packet length variance to maintain detection sensitivity.
