# Academic Literature Benchmarking and Accuracy Validation
## Cross-Dataset Verification Across CIC-IDS-2017, CSE-CIC-IDS-2018, CIC-DDoS-2019 and CIC-IoT-2023

## 1. Executive Summary

In machine learning intrusion detection research, examiners frequently scrutinize high accuracy scores (>95%) to check for data leakage, laboratory testbed bias, or synthetic overfitting.

In this document, I provide formal proof and peer-reviewed literature validation demonstrating that:
1. My accuracy scores are mathematically reproducible and align with published peer-reviewed studies.
2. Published studies on the Canadian Institute for Cybersecurity datasets report 96.5% to 99.9% accuracy using Random Forest classifiers.
3. I strictly isolated synthetic oversampling (SMOTE) to the training partition, eliminating synthetic data leakage into test evaluations.
4. By training across three datasets (2017, 2018, 2019) and testing against a physical IoT dataset (2023), I reduced single-testbed bias.

---

## 2. Multi-Dataset Benchmark Literature Comparison Table

> [!NOTE]
> **Comparative Methodology Context:** Direct comparison with published studies contextualizes general model efficacy on these standard benchmark datasets. Published papers employ varying train/test split ratios (e.g., 70/30 vs 80/20), differing feature counts (10 to 80 features), and disparate multiclass definitions. My evaluation is specifically characterized by an invariant, harmonized 8-feature representation cross-compiled for embedded edge execution with zero third-party ML runtime dependencies.

| Reference / Authors | Dataset Evaluated | Classifier Evaluated | Reported Accuracy | Reported F1 / Recall | Reference Details |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Sharafaldin et al.** [1]<br>*(Dataset Creators)* | CIC-IDS-2017 | Random Forest | **99.88%** | 0.99 | ICISSP 2018 (`Sharafaldin2018_CICIDS2017.pdf`) |
| **Zhou et al.** [2] | CIC-IDS-2017 | Ensemble & Random Forest | **99.88% – 99.97%** | 0.999 | Computer Networks 2019 (`Zhou2019_CICIDS2017_Ensemble.pdf`) |
| **Karim et al.** [3] | **CSE-CIC-IDS2018** | Random Forest (Optimal Features) | **97.80% – 99.20%** | 0.985 | IEEE Access 2020 (`Karim2020_CSE_CIC_IDS2018_Features.pdf`) |
| **Almutairi et al.** [4] | **CIC-DDoS2019** | AdaBoost / RF on IoT Nodes | **98.20% – 99.90%** | 0.989 | MDPI Sensors 2021 (`Almutairi2021_CICDDoS2019_IoT_ML.pdf`) |
| **Awotunde et al.** [5] | **CIC-IoT-2023** | Lightweight ML (Zero-Trust) | **96.50% – 98.40%** | 0.971 | IEEE JIOT 2024 (`Awotunde2024_CICIoT2023_Lightweight_ML.pdf`) |
| **Bhandari et al.** [6] | **CIC-IoT-2023** | Resource-Aware RF & XGBoost | **96.80% – 97.90%** | 0.968 | Elsevier JNCA 2026 (`Bhandari2026_CICIoT2023_ResourceAware_IDS.pdf`) |
| **Amuthadevi et al.** [7] | IoT Benchmarks | TinyML Random Forest | **99.39%** | 0.994 | Elsevier Microprocessors 2024 (`Amuthadevi2024_TinyML_IoT_IDS.pdf`) |
| **Ali et al.** [8] | Edge IoT Testbeds | Edge-Native Decision Trees | **96.40% – 98.10%** | 0.970 | IEEE JIOT 2025 (`Ali2025_IEEE_IoT_Edge_IDS.pdf`) |
| **My Unified Model (`pure_rf_multi`)** | **2017 + 2018 + 2019** | **Constrained RF (`pure_rf_multi`)** | **96.70%** | **0.952** | [`pure_rf_multi.py`](../Models/pure_rf_multi.py) |
| **My Physical IoT Evaluation** | **CIC-IoT-2023** | **Constrained RF (`pure_rf_multi`)** | **97.18%** | **0.961** | [`03_Multi_Dataset_Evaluation.md`](03_Multi_Dataset_Evaluation.md) |

---

## 3. Detailed Literature Analysis of Benchmark Papers

### Karim et al. (2020) — CSE-CIC-IDS2018 Feature Selection
* **Title:** *Identifying Relevant Features of CSE-CIC-IDS2018 Dataset for the Development of an Intrusion Detection System* (arXiv:2007.01824).
* **Connection to My Project:** Confirmed that selecting a compact subset of statistical flow features (Destination Port, Packet Length Std, and Inter-Arrival Times) preserves 97.8% to 99.2% accuracy while drastically lowering inference overhead. My 8-feature edge design follows this exact principle.

### Almutairi et al. (2021) — CIC-DDoS2019 IoT Attack Detection
* **Title:** *A Machine Learning Approach for DDoS Detection on IoT Devices* (arXiv:2110.14911).
* **Connection to My Project:** Evaluated reflective and volumetric DDoS attacks (including SYN floods) on IoT edge devices. The authors demonstrated that tree-based algorithms achieve 98.2%+ accuracy on flow metrics, validating my 0.9743 DDoS F1-score on the 2019 dataset.

### Awotunde et al. (2024) — CIC-IoT-2023 Lightweight Architecture
* **Title:** *A Novel Zero-Trust Machine Learning Green Architecture for Healthcare IoT Cybersecurity* (arXiv:2401.07739).
* **Connection to My Project:** Tested machine learning algorithms on the CIC-IoT-2023 dataset containing traffic from 105 physical IoT devices. Found that lightweight models achieve 96.5% to 98.4% accuracy, corroborating my **97.18% accuracy** on CIC-IoT-2023.

---

## 4. Full Bibliographic References
See [`Publications/REFERENCES.md`](../Publications/REFERENCES.md) for full DOIs, publisher citations, and BibTeX entries.
