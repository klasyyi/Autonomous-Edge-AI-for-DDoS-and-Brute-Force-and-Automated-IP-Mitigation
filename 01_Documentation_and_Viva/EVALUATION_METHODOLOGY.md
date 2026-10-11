# FYP Technical Report: Machine Learning Evaluation Methodology

**Project:** Autonomous TinyML Edge-Security Gateway  
**Model Architecture:** Constrained Random Forest (`n_estimators=20`, `max_depth=10`)  
**Cross-Compilation Tool:** `m2cgen` (Model-to-Code Generator)  
**Dataset:** Canadian Institute for Cybersecurity CIC-IDS-2017 Benchmark  

---

## 1. Overview & Research Objective

The objective of the machine learning pipeline is to train a multi-threat intrusion detection model capable of classifying live network flows into three distinct categories:
1. **`BENIGN`**: Normal legitimate network traffic (web browsing, DNS, SSH management).
2. **`DDoS`**: Volumetric and application-layer denial-of-service traffic (SYN floods, HTTP GET floods).
3. **`SSH-Patator`**: Brute-force credential guessing attacks directed against Port 22.

To deploy on a resource-constrained **Raspberry Pi 4 (ARM Cortex-A72)**, the methodology enforces a **TinyML constraint**: the classifier must execute in sub-millisecond time ($< 0.10\text{ ms}$) without requiring heavyweight runtime libraries (`scikit-learn`, `numpy`, or `pandas`).

---

## 2. Dataset Synthesis & Data Cleaning

The training corpus was assembled by integrating two distinct day captures from the benchmark CIC-IDS-2017 dataset:
* **Friday Afternoon Capture:** Contains real-world benign baseline traffic along with LOIC and synthetic volumetric DDoS attacks (`Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`).
* **Tuesday Capture:** Contains benign background activity alongside automated SSH brute-force attacks (`Tuesday-WorkingHours.pcap_ISCX.csv`).

### Data Cleaning Protocol:
1. **Header Sanitization:** Column labels were stripped of leading and trailing whitespace artifacts (`df.columns.str.strip()`).
2. **Infinite and Missing Value Elimination:** Real-world flow calculation tools occasionally compute infinite rates when flow durations approach zero. All `np.inf` and `-np.inf` values were replaced with `np.nan` and dropped:
   $$\text{DropRows}(X) \iff \exists j \text{ s.t. } X_{i,j} \in \{\text{NaN}, \infty, -\infty\}$$
3. **Class Isolation:** The dataset was filtered to retain only the targeted evaluation classes: `['BENIGN', 'DDoS', 'SSH-Patator']`.

---

## 3. Mathematical Feature Selection (The 8 Core Features)

Rather than evaluating all 84 raw features—which induces severe memory swapping on ARM processors—feature importance analysis distilled the flow space down to **8 core mathematical features**:

| Feature Name | Type | Mathematical / Networking Rationale |
| :--- | :---: | :--- |
| **`Destination Port`** | Integer | Discriminates service targets (e.g., Port 22 for SSH-Patator, Port 80/443 for HTTP DDoS, ephemeral ports). |
| **`Bwd Packet Length Std`** | Float ($\mu s$) | Standard deviation of response payload sizes. In volumetric floods, the server rarely responds, driving this value toward $0$. |
| **`SYN Flag Count`** | Integer | Counts synchronization handshake packets; volumetric SYN floods exhibit abnormally high ratios relative to ACK packets. |
| **`Flow IAT Mean`** | Float ($\mu s$) | Mean packet Inter-Arrival Time within the flow. Automated botnets fire packets in rapid bursts ($<1000\mu s$), whereas human activity exhibits variable pauses. |
| **`Total Fwd Packets`** | Integer | Cumulative count of outbound packets transmitted by the source IP. |
| **`Flow Duration`** | Float ($\mu s$) | Total lifetime of the bidirectional TCP session. |
| **`Fwd Packet Length Mean`** | Float (Bytes) | Average payload size of client packets. Brute-force probes send small, repetitive authentication strings. |
| **`Init_Win_bytes_forward`** | Integer | Size of initial TCP window advertisement, acting as an OS/client network stack fingerprint. |

---

## 4. Train/Test Separation & Class Balancing (SMOTE)

### The Data Leakage Prevention Guarantee
A critical academic criterion is avoiding data leakage. If over-sampling techniques like SMOTE are executed before dataset partitioning, synthetic samples bleed into the test set, creating artificially inflated metrics.

1. **Partitioning:** The dataset was strictly partitioned prior to any data transformation:
   - **Training Set (80%):** 530,738 flows
   - **Unseen Testing Vault (20%):** 132,685 flows
   - Random seed locked to `random_state = 42` for exact reproducibility.
2. **Subsampling:** To prevent majority-class domination and excessive memory consumption during synthetic calculation, the `BENIGN` training pool was capped at 50,000 samples.
3. **SMOTE Execution:** The Synthetic Minority Over-sampling Technique (SMOTE) was applied **exclusively to the training split**:
   $$x_{new} = x_i + \lambda \times (x_{zi} - x_i), \quad \lambda \sim U(0, 1)$$
   This generated synthetic feature vectors for `DDoS` and `SSH-Patator` solely within the training domain.
4. **Validation Integrity:** The 20% test fold remained untouched, containing 100% natural, unaugmented network traffic.

---

## 5. Model Architecture & TinyML Compilation

### Hyperparameter Bounds
* **Classifier:** `RandomForestClassifier`
* `n_estimators = 20`: Selected via grid search to balance ensemble diversity against inference latency.
* `max_depth = 10`: Enforced to bound the depth of binary splits, preventing memorization of source IP addresses or transient timestamps.
* `n_jobs = -1`: Utilized all available CPU cores during offline training.

### Cross-Compilation with `m2cgen`
The trained Scikit-Learn model was compiled via `m2cgen` into `pure_rf_v2.py`. 
* Converts binary decision trees into nested conditional expressions (`if/else`).
* Eliminates all dependency on `numpy`, `scipy`, and `scikit-learn` on the Raspberry Pi.
* Slashes per-flow classification latency to **$0.08\text{ ms}$**.

---

## 6. Formal Evaluation Results

Evaluated against the **20% unseen test split (132,685 real-world flows)**:

### Classification Report:
```text
               precision    recall  f1-score   support

      BENIGN       1.00      1.00      1.00    106071
        DDoS       1.00      1.00      1.00     25478
 SSH-Patator       0.99      1.00      1.00      1136

    accuracy                           1.00    132685
   macro avg       1.00      1.00      1.00    132685
weighted avg       1.00      1.00      1.00    132685
```

* **Overall Accuracy:** **99.98%**
* **Macro Precision:** 0.997 ($\approx 1.00$)
* **Macro Recall:** 0.999 ($\approx 1.00$)
* **Macro F1-Score:** 0.998 ($\approx 1.00$)
* **Average Inference Latency:** **0.08ms per flow**
