# Academic Literature Benchmarking: Hardware Efficiency and Edge Resource Metrics
## 1. Executive Summary

In this report, I provide an empirical, publication-backed comparison of my **Autonomous Edge-AI Security Gateway** against published research papers that evaluated intrusion detection systems on edge hardware (Raspberry Pi, microcontrollers) and cloud environments.

Rather than relying on theoretical comparisons, every benchmark cited in this document is verified against peer-reviewed papers archived in the [`Publications/`](../Publications/) directory.

---

## 2. Hardware and Efficiency Benchmark Matrix

> [!NOTE]
> **Platform & Architecture Context:** The Raspberry Pi 4 Model B is a Single Board Computer (Quad-Core ARM Cortex-A72 @ 1.5 GHz) rather than a microcontroller. While lightweight deep learning runtimes (e.g., TFLite or ONNX Runtime) can execute on a Pi 4, my pure-Python cross-compiled approach (`m2cgen`) was chosen for three concrete engineering reasons: (1) eliminating all C-shared library and ABI version conflicts, (2) minimizing memory overhead to **~24.4 MB RSS**, and (3) enabling transparent, line-by-line auditability of decision logic.

| Paper & Authors | Publication Venue & Year | Evaluated Platform | Detection Approach | Measured Latency / Response Time | Measured Resource Utilization | Reported Accuracy / F1 | Proof File in Repo |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Cherukuri** [1] | *IJFMR*, 2024 | Centralized Cloud Server vs. Edge Node | Cloud vs. Edge Real-Time AI | **Cloud: 100 – 200 ms**<br>**Edge: 10 – 20 ms** | Cloud: 1k–10k tasks/s<br>Edge: 100–1k tasks/s | Security: Cloud 6/10<br>Edge 7/10 | [`Cherukuri2024_Edge_vs_Cloud_AI.pdf`](../Publications/Cherukuri2024_Edge_vs_Cloud_AI.pdf) |
| **Ali et al.** [2] | *IEEE IoT Journal*, 2025 | Edge Nodes / Raspberry Pi | Deep Transfer Learning (ResNet / VGG-RED) | **High Latency** (Multi-tensor forward passes) | High Edge CPU saturation; large neural weight footprint | 95.97% (AdaBoost)<br>73.70% (RF baseline) | [`Ali2025_IEEE_IoT_Edge_IDS.pdf`](../Publications/Ali2025_IEEE_IoT_Edge_IDS.pdf) |
| **Amuthadevi et al.** [3] | *Sustainable Energy*, 2024 | Energy-Constrained IoT Edge Devices | TinyML (Random Forest, AdaBoost) | **~10 – 50 ms** window on MCU | Constrained power; traditional RF incurs memory overhead on MCUs | 99.39% Accuracy<br>99.45% F1-score | [`Amuthadevi2024_TinyML_IoT_IDS.pdf`](../Publications/Amuthadevi2024_TinyML_IoT_IDS.pdf) |
| **Hafid & Ezzouhairi** [4] | *IEEE Conference*, 2024 | IoT Edge Gateway Architecture | Random Forest, Decision Tree | **15 – 35 ms** flow ingestion | High edge memory cited without model compression | 86.0% Accuracy<br>89.0% Recall | [`Hafid2024_IEEE_IoT_Edge_IDS.pdf`](../Publications/Hafid2024_IEEE_IoT_Edge_IDS.pdf) |
| **Standard Edge Python Deployment** [5] | Local Benchmark Baseline | Raspberry Pi 4 Model B (ARM Cortex-A72) | Standard Scikit-Learn `.pkl` Random Forest | **15.20 ms** per flow *(Framework overhead)* | **25% – 35% CPU**<br>140 – 180 MB RAM | 99.98% Accuracy | [`history_findings_and_tradeoffs.txt`](history/history_findings_and_tradeoffs.txt) (Local test log) |
| **My Project (Autonomous Gateway)** | **Current FYP Implementation** | **Raspberry Pi 4 Model B (ARM Cortex-A72)** | **Compiled Pure RF (`m2cgen`) + Deterministic L4 Filter** | **0.021 ms** (pure ML inference)<br>**0.08–0.17 ms** (end-to-end) | **0.0% – 0.3% Idle CPU** (Peak 15–20% burst)<br>**~24.4 MB RSS**, **1.05 MB Model** | **96.70% Multi-Dataset**<br>**97.18% IoT Accuracy** | Live Prototype ([`Gateway/dashboard.py`](../Gateway/dashboard.py) and [`Gateway/pure_rf_multi.py`](../Gateway/pure_rf_multi.py)) |

---

## 3. In-Depth Analysis of Comparative Literature

### 1. Cloud Latency Fails Real-Time Defense (Cherukuri, 2024)
* **Citation:** Cherukuri, B. R. (2024). *Edge Computing vs. Cloud Computing: A Comparative Analysis for Real-Time AI Applications*, IJFMR, 6(5).
* **Published Findings:** Cloud-based AI experiences **100 to 200 ms round-trip latency**, whereas local edge processing achieves **10 to 20 ms**.
* **Relevance to My Project:** Volumetric DDoS attacks transmit thousands of packets per second. A 150 ms cloud round-trip delay allows network buffers to saturate before a cloud API can respond. My gateway executes end-to-end classification and mitigation locally in **0.08 ms to 0.17 ms**, mitigating threats in real time.

### 2. Deep Learning Overburdens Resource-Constrained Edge Nodes (Ali et al., 2025)
* **Citation:** Ali, Z. et al. (2025). *Deep Transfer Learning for Intrusion Detection in Edge Computing Scenarios*, IEEE Internet of Things Journal, 12(21).
* **Published Findings:** While deep transfer learning achieves high accuracy, continuous tensor operations and neural backpropagation produce substantial memory and CPU strain on edge processors.
* **Relevance to My Project:** Running heavy deep neural networks on an embedded ARM Cortex-A72 requires floating-point tensor engines (PyTorch / ONNX) that consume 60% to 95% CPU, causing thermal throttling. My constrained Random Forest operates at **0.0% to 0.3% CPU during routine sniffing** with zero thermal degradation.

### 3. TinyML Feasibility on Energy-Constrained Hardware (Amuthadevi et al., 2024)
* **Citation:** Amuthadevi, C. et al. (2024). *TinyML-based intrusion detection systems for sustainable and energy-constrained IoT devices*, Sustainable Energy, 7.
* **Published Findings:** The authors confirmed that Random Forest delivers 99.39% accuracy for IoT intrusion detection, but emphasized that standard implementations consume excessive memory on edge nodes unless compressed.
* **Relevance to My Project:** I addressed the exact limitation noted by Amuthadevi et al. by using `m2cgen` to decompile my trained ensemble into pure Python mathematical branching logic, reducing process memory consumption to ~24.4 MB RSS.

---

## 4. Key Architectural Innovations

### Innovation 1: Overcoming the 15 ms Python Framework Bottleneck
When running standard scikit-learn `.pkl` models on the Raspberry Pi 4, inference required approximately 15.20 ms per sample. Profiling demonstrated that the matrix mathematics completed in under 0.1 ms, but Python spent over 15 ms performing numpy array shape validation and dynamic type checking on ARM. By cross-compiling the model into pure Python `if/else` logic (`pure_rf_multi.py`, 1.05 MB), I eliminated all framework overhead and achieved **0.021 ms latency**.

### Innovation 2: Two-Tier Hierarchical Defense Architecture
To prevent high-rate volumetric floods from exhausting edge memory, I designed a two-tier architecture:
1. **Tier 1 (L4 Rate Pre-Filter):** Evaluates incoming SYN frequency across a 3-second sliding window. Rapid floods (>30 SYNs) across randomized ephemeral ports are immediately dropped at Layer 4, saving CPU.
2. **Tier 2 (L7 TinyML Behavioral Engine):** Moderate and subtle connection flows pass to the compiled Random Forest (`pure_rf_multi.py`) for multi-variate feature classification (e.g., detecting SSH brute force).

---

## 5. Full Bibliographic References
See [`Publications/REFERENCES.md`](../Publications/REFERENCES.md) for full DOIs, publisher citations, and BibTeX entries.
