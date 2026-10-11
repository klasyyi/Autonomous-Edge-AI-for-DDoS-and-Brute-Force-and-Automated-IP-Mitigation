# Machine Learning Evaluation Methodology
## 1. Overview and Research Objective

In this project, my objective was to design, train, and validate a multi-threat intrusion detection model capable of classifying live network flows into three distinct categories:
1. **`BENIGN`**: Normal network traffic (web browsing, DNS, SSH management).
2. **`DDoS`**: Volumetric and application-layer denial-of-service traffic (SYN floods, HTTP GET floods).
3. **`SSH-Patator`**: Brute-force credential guessing attacks directed against Port 22.

To deploy on my resource-constrained **Raspberry Pi 4 (ARM Cortex-A72)**, I enforced a strict **TinyML constraint**: the classifier must execute in sub-millisecond time (< 0.10 ms) without requiring heavyweight runtime libraries (`scikit-learn`, `numpy`, or `pandas`).

---

## 2. Dataset Synthesis and Data Cleaning

I assembled the training corpus by integrating two distinct day captures from the benchmark CIC-IDS-2017 dataset:
- **Friday Afternoon Capture:** Contains real-world benign baseline traffic along with LOIC and synthetic volumetric DDoS attacks (`Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`).
- **Tuesday Capture:** Contains benign background activity alongside automated SSH brute-force attacks (`Tuesday-WorkingHours.pcap_ISCX.csv`).

### Data Cleaning Protocol:
1. **Header Sanitization:** I stripped column labels of leading and trailing whitespace artifacts (`df.columns.str.strip()`).
2. **Infinite and Missing Value Elimination:** Flow calculation tools compute infinite rates when flow durations approach zero. I replaced all `np.inf` and `-np.inf` values with `np.nan` and dropped them:
   $$\text{DropRows}(X) \iff \exists j \text{ s.t. } X_{i,j} \in \{\text{NaN}, \infty, -\infty\}$$
3. **Class Isolation:** I filtered the dataset to retain only my targeted evaluation classes: `['BENIGN', 'DDoS', 'SSH-Patator']`.

---

## 3. Feature Selection (The 8 Core Features)

Rather than evaluating all 84 raw features—which induces severe memory swapping on ARM processors—I conducted feature importance analysis and distilled the flow space down to **8 core mathematical features**:

| Feature Name | Type | Mathematical and Networking Rationale |
| :--- | :---: | :--- |
| **`Destination Port`** | Integer | Discriminates service targets (e.g., Port 22 for SSH-Patator, Port 80/443 for HTTP DDoS, ephemeral ports). |
| **`Bwd Packet Length Std`** | Float ($\mu s$) | Standard deviation of response payload sizes. In volumetric floods, the server rarely responds, driving this value toward 0. |
| **`SYN Flag Count`** | Integer | Counts synchronization handshake packets; volumetric SYN floods exhibit abnormally high ratios relative to ACK packets. |
| **`Flow IAT Mean`** | Float ($\mu s$) | Mean packet Inter-Arrival Time within the flow. Automated botnets fire packets in rapid bursts (< 1000 $\mu s$), whereas human activity exhibits variable pauses. |
| **`Total Fwd Packets`** | Integer | Cumulative count of outbound packets transmitted by the source IP. |
| **`Flow Duration`** | Float ($\mu s$) | Total lifetime of the bidirectional TCP session. |
| **`Fwd Packet Length Mean`** | Float (Bytes) | Average payload size of client packets. Brute-force probes send small, repetitive authentication strings. |
| **`Init_Win_bytes_forward`** | Integer | Size of initial TCP window advertisement, acting as an OS/client network stack fingerprint. |

---

## 4. Train/Test Separation and Class Balancing (SMOTE)

### Data Leakage Prevention Guarantee
A critical requirement in my methodology was avoiding data leakage. If over-sampling techniques like SMOTE are executed before dataset partitioning, synthetic samples bleed into the test set, creating artificially inflated metrics.

1. **Partitioning:** I strictly partitioned the dataset prior to any data transformation:
   - **Training Set (80%):** 530,738 flows
   - **Unseen Testing Vault (20%):** 132,685 flows
   - I locked the random seed to `random_state = 42` for exact reproducibility.
2. **Subsampling:** To prevent majority-class domination and excessive memory consumption during synthetic calculation, I capped the `BENIGN` training pool at 50,000 samples.
3. **SMOTE Execution:** I applied the Synthetic Minority Over-sampling Technique (SMOTE) exclusively to the training split:
   $$x_{new} = x_i + \lambda \times (x_{zi} - x_i), \quad \lambda \sim U(0, 1)$$
   This generated synthetic feature vectors for `DDoS` and `SSH-Patator` solely within the training domain.
4. **Validation Integrity:** My 20% test fold remained untouched, containing 100% natural, unaugmented network traffic.

---

## 5. Model Architecture and TinyML Compilation

### Hyperparameter Bounds
- **Classifier:** `RandomForestClassifier`
- `n_estimators = 20`: Selected via grid search to balance ensemble diversity against inference latency.
- `max_depth = 10`: Enforced to bound the depth of binary splits, preventing memorization of source IP addresses or transient timestamps.
- `n_jobs = -1`: Utilized all available CPU cores during offline training.

### Cross-Compilation with `m2cgen`
I cross-compiled the trained Scikit-Learn model via `m2cgen` into native Python (`pure_rf_v2.py`):
- Converts binary decision trees into nested conditional expressions (`if/else`).
- Eliminates all dependency on `numpy`, `scipy`, and `scikit-learn` on the Raspberry Pi.
- Slashes per-flow classification latency to **0.08 ms**.

---

## 6. Formal Evaluation Results

Evaluated against my **20% unseen test split (132,685 real-world flows)**:

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

- **Overall Accuracy:** **99.98%**
- **Macro Precision:** 0.997 (~1.00)
- **Macro Recall:** 0.999 (~1.00)
- **Macro F1-Score:** 0.998 (~1.00)
- **Average Inference Latency:** **0.08 ms per flow**
