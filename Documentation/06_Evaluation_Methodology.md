# Machine Learning Evaluation Methodology and Experimental Design

## 1. Overview and Research Objective

In this project, my objective was to design, train, evaluate, and deploy an autonomous Network Intrusion Detection System (NIDS) running on a physical **Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.5 GHz, 4GB RAM)**.

The classification engine identifies network traffic flows into three distinct behavioral classes:
1. **`BENIGN`**: Legitimate network sessions (HTTP/HTTPS web browsing, DNS queries, legitimate SSH administration).
2. **`DDoS`**: Volumetric TCP SYN floods and application-layer denial-of-service traffic.
3. **`SSH-Patator`**: Brute-force credential guessing probes directed against Port 22.

### Edge Computational Constraints
Deploying machine learning models directly onto embedded edge nodes introduces strict operational constraints:
- **Sub-Millisecond Latency:** Inference must execute in under 0.10 ms per flow to avoid packet backlog during traffic bursts.
- **Dependency Elimination:** Heavy runtime libraries (`scikit-learn`, `numpy`, `scipy`, `pandas`) must be eliminated from the edge environment to avoid runtime conflicts and multi-hundred-megabyte disk overhead.
- **Low Memory Footprint:** The classification process must operate within minimal system RAM (~24.4 MB RSS) without inducing memory paging.

---

## 2. Experimental Evolution: Two-Phase Methodology

To ensure scientific validity, I conducted my research across two distinct phases:

### Phase 1: Baseline Single-Dataset Investigation and Discovery of Testbed Bias
In my initial experiments, I trained a 20-tree Random Forest classifier (`pure_rf_v2.py`) solely on the **CIC-IDS-2017** benchmark. While this model achieved **99.98% accuracy** and 0.08 ms latency when evaluated against a 20% holdout split of CIC-IDS-2017 (132,685 flows), evaluating it against unseen traffic from **CSE-CIC-IDS-2018** resulted in an immediate collapse to **22.64% accuracy**.

**Root Cause Analysis:** Single-dataset training caused the decision boundaries to overfit to static laboratory artifacts—such as fixed subnet IP ranges, synthetic inter-arrival time constants, and uniform background traffic—rather than learning invariant protocol signatures.

### Phase 2: Universal Multi-Dataset Harmonization and Physical IoT Validation
To reduce testbed bias, I engineered a cross-dataset feature harmonization pipeline combining three benchmark years (**CIC-IDS-2017**, **CSE-CIC-IDS-2018**, and **CIC-DDoS-2019**), yielding a unified corpus of **115,308 network flows**. I then validated the resulting model against **26,592 flows from the physical 105-device `CIC-IoT-2023` testbed**, demonstrating cross-dataset generalization.

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
$$\text{F1}_c = 2 \times \frac{\text{Precision}_c \times \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

### 5. Macro-Averaged F1-Score
$$\text{Macro F1} = \frac{1}{|C|} \sum_{c \in C} \text{F1}_c$$
Macro-averaging weights all three classes equally, preventing dominant classes (such as DDoS floods) from masking detection failures on minority classes (such as SSH brute force).

### 6. False Positive Rate (FPR) on Benign Traffic
$$\text{FPR}_{\text{benign}} = \frac{FP_{\text{benign}}}{FP_{\text{benign}} + TN_{\text{benign}}}$$
This metric directly quantifies the risk of inadvertent denial-of-service against legitimate network users.

---

## 4. Feature Selection and Schema Standardization

To reconcile schema disparities across multi-year captures while conforming to embedded hardware constraints, I reduced the high-dimensional feature space (80+ columns) to **8 invariant features**:

| Index | Feature Name | Network Significance | Mathematical Operation |
| :---: | :--- | :--- | :--- |
| **0** | `Destination Port` | Identifies targeted services (e.g., Port 22 for SSH, Port 80 for HTTP). | Discrete Integer |
| **1** | `Bwd Packet Length Std` | Measures variance in backward packet sizes; attacks exhibit near-zero variance. | Standard Deviation ($\sigma$) |
| **2** | `SYN Flag Count` | Tracks TCP connection initiation packets; high values indicate SYN floods. | Summation ($\sum$) |
| **3** | `Flow IAT Mean` | Average microsecond delay between packets; floods exhibit microsecond intervals. | Arithmetic Mean ($\mu$) |
| **4** | `Total Fwd Packets` | Volume of outgoing packets transmitted in the flow window. | Count ($N$) |
| **5** | `Flow Duration` | Total elapsed duration of the flow in microseconds. | Time Delta ($\Delta t$) |
| **6** | `Fwd Packet Length Mean`| Average payload size of forward packets. | Arithmetic Mean ($\mu$) |
| **7** | `Init_Win_bytes_forward`| Initial TCP window advertisement; reveals OS stack fingerprint. | Header Field |

---

## 5. Class Balancing Protocol: Synthetic Minority Over-sampling (SMOTE)

In raw intrusion captures, benign traffic and volumetric floods vastly outnumber low-rate brute-force probes, creating extreme class imbalance.

### Train-Test Isolation Protocol
To prevent synthetic data contamination and eliminate data leakage:
1. The unified dataset (115,308 flows) was partitioned into an **80% training set (92,246 flows)** and a **20% test set (23,062 flows)** using stratified sampling.
2. SMOTE was applied **strictly to the 80% training partition**:
   $$\mathbf{x}_{\text{new}} = \mathbf{x}_i + \lambda \times (\mathbf{x}_{zi} - \mathbf{x}_i), \quad \lambda \in [0, 1]$$
3. The 20% test partition remained completely unaugmented natural network traffic.

---

## 6. Model Optimization and Pure-Python Cross-Compilation

Using `m2cgen`, I cross-compiled the trained ensemble into pure Python branching code:
- Converts all 25 decision trees into deterministic nested `if/else` statements.
- **Zero Runtime Dependencies:** Requires bare Python 3 with no imports of `numpy`, `scipy`, or `scikit-learn` on the edge gateway.
- **Compiled File Size:** Exactly **1.05 MB**.
- **Pure ML Inference Latency:** **0.021 ms per flow** (~47,600 classifications per second).
- **Process Memory Footprint:** **~24.4 MB RSS** on the Raspberry Pi 4.

---

## 7. Formal Experimental Evaluation Results

### A. Universal Multi-Dataset Holdout (23,062 Unseen Flows)
Evaluated across unseen test flows spanning CIC-IDS-2017, CSE-CIC-IDS-2018, and CIC-DDoS-2019:

| Traffic Class | Precision | Recall | F1-Score | Test Support (Flows) |
| :--- | :---: | :---: | :---: | :---: |
| **BENIGN** | 0.9975 | 0.9973 | 0.9974 | 5,282 |
| **DDoS** | 0.9987 | 0.9511 | 0.9743 | 14,958 |
| **SSH-Patator** | 0.7941 | 0.9950 | 0.8833 | 2,822 |
| **Overall Accuracy** | - | - | **0.9670 (96.70%)** | **23,062** |
| **Macro Average** | **0.9301** | **0.9812** | **0.9517** | **23,062** |
| **Weighted Average** | **0.9734** | **0.9670** | **0.9685** | **23,062** |

### B. Architecture Baseline Comparisons: "Why Machine Learning?"

To evaluate whether simpler algorithms or static heuristics suffice, I benchmarked four distinct architectures on the same test corpus:

| Model Architecture | Accuracy | Macro F1 | Benign FPR | Latency | Operational Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Static Heuristic Threshold** | 37.11% | 0.4422 | **36.01%** | 0.0647 ms | **Unusable:** 36% false alarms on legitimate traffic. |
| **2. Logistic Regression (L2)** | 76.25% | 0.7047 | **44.37%** | 0.0003 ms | **Unusable:** Linear boundaries fail on non-linear network features. |
| **3. Shallow Decision Tree (depth=5)** | 93.60% | 0.9180 | **13.22%** | 0.0002 ms | **Sub-optimal:** 13% false alarms still risks network disruption. |
| **4. Proposed Random Forest (depth=12)** | **97.12%** | **0.9608** | **0.19%** | **0.0018 ms** | **Optimal:** Suppresses false alarms to < 0.2% while detecting threats. |

### C. Dedicated Physical IoT Testbed Evaluation (`CIC-IoT-2023`)
Evaluated on **26,592 unseen flows** collected from 105 physical smart home and edge devices:
- **Overall IoT Accuracy:** **97.18%**
- **DDoS Precision / Recall / F1:** **1.00 / 1.00 / 1.00**
- **Benign Precision / Recall / F1:** **0.97 / 0.94 / 0.95**
- **Brute-Force Recall:** **0.51**

---

## 8. Empirical Hardware Evaluation: Soak Testing vs. Volumetric Stress Testing

To establish empirical rigor, I separated hardware evaluation into two distinct testing protocols:

### A. Extended Hardware Longevity & Memory Stability Soak Test
* **Objective:** Validate daemon persistence, memory stability, and heap isolation over multi-hour headless operation.
* **Execution:** Continuous physical hardware execution on the Raspberry Pi 4 under ambient local traffic (~1 pkt/sec) recorded at 5-minute telemetry intervals (`history_stress_test_log.csv`).
* **Verified Findings:**
  - **Process RAM Footprint:** The Python daemon consumed strictly **~24.4 MB RSS**. Total Raspberry Pi OS system memory utilization remained flat between **10.1% and 11.6%** (approx. 400 MB to 460 MB of 4 GB RAM, including kernel network buffers).
  - **Memory Leakage:** 0% growth after initial socket buffer allocation, confirming zero memory leaks.
  - **Idle Processor Draw:** CPU load stayed between **0.0% and 0.3%**.
  - **Memory Bounding:** Protected by in-memory sliding-window TTL eviction (60-second inactivity prune).

### B. Active Volumetric Attack Stress Test
* **Objective:** Stress network buffers, measure packet handling thresholds, and quantify autonomous mitigation speed under attack.
* **Execution:** Multi-threaded synthetic flood generation using `simulate_traffic.py --mode stress` (1,000+ packets/sec bursts across randomized ports).
* **Measured Latency Disaggregation:**
  1. **Pure Machine Learning Inference Latency:** **0.021 ms** (pure-Python decision tree execution via `m2cgen`).
  2. **End-to-End Ingestion-to-Mitigation Latency:** **0.08 ms to 0.17 ms** (including raw packet capture, 5-tuple table update, and Linux kernel `iptables` drop rule execution).

---

## 9. Threat Model, Topology, and Operating Boundaries

### A. Network Topology
The gateway operates as a **Local Edge Security Appliance (Bump-in-the-Wire)** deployed at the network perimeter protecting downstream IoT devices on interface `eth0`.
* **In-Scope Protection:** Protects local hosts and IoT nodes against host resource-exhaustion attacks (CPU/RAM exhaustion from TCP SYN connection queues and SSH credential brute force).
* **Out-of-Scope Limitation:** An edge device cannot prevent upstream ISP bandwidth saturation if an attacker floods the physical access pipe with gigabit-scale traffic; upstream pipe flooding requires ISP-level BGP blackholing or scrubbers.

### B. Mitigation Safety and Anti-Spoofing Controls
To prevent attackers from abusing automated mitigation (e.g., spoofing trusted IPs to cause collateral denial of service):
1. **Permanent Whitelist:** Localhost, default gateway (`192.168.137.1`), core DNS servers (`8.8.8.8`, `1.1.1.1`), and broadcast addresses are whitelisted and never blocked.
2. **Block Rule TTL (300 Seconds):** Firewall drop rules automatically expire and unblock after 5 minutes, preventing permanent lockout of transient IPs.
3. **Maximum Rule Cap (500 Rules):** Capped at 500 active `iptables` rules to prevent kernel netfilter chain latency degradation.
4. **Transport Focus:** Currently monitors TCP session flows; high-rate UDP amplification floods are delegated to kernel-level rate limits.
