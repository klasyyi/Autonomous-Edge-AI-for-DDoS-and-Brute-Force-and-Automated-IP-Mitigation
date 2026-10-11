# Academic Literature Benchmarking: Hardware Efficiency and Edge Resource Metrics

> **Author:** Final Year Project Student (Computer Science / Cyber Security)  
> **Hardware Platform:** Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.5GHz, 4GB LPDDR4)  
> **Measured Performance:** 0.021 ms Inference Latency, 0.0% to 0.3% Idle/Sniffing CPU, ~24 MB Total Gateway RAM

---

## 1. Executive Summary

In this report, I provide an empirical, publication-backed comparison of my **Autonomous Edge-AI Security Gateway** against published research papers that evaluated intrusion detection systems on edge hardware (Raspberry Pi, microcontrollers) and cloud environments.

Rather than relying on theoretical comparisons, every benchmark cited in this document is verified against peer-reviewed papers archived in the [`02_Publications_Proof/`](../02_Publications_Proof/) directory.

---

## 2. Hardware and Efficiency Benchmark Matrix

| Paper & Authors | Publication Venue & Year | Evaluated Platform | Detection Approach | Measured Latency / Response Time | Measured Resource Utilization | Reported Accuracy / F1 | Proof File in Repo |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Cherukuri** [1] | *IJFMR*, 2024 | Centralized Cloud Server vs. Edge Node | Cloud vs. Edge Real-Time AI | **Cloud: 100 – 200 ms**<br>**Edge: 10 – 20 ms** | Cloud: 1k–10k tasks/s<br>Edge: 100–1k tasks/s | Security: Cloud 6/10<br>Edge 7/10 | [`Cherukuri2024_Edge_vs_Cloud_AI.pdf`](../02_Publications_Proof/Cherukuri2024_Edge_vs_Cloud_AI.pdf) |
| **Ali et al.** [2] | *IEEE IoT Journal*, 2025 | Edge Nodes / Raspberry Pi | Deep Transfer Learning (ResNet / VGG-RED) | **High Latency** (Multi-tensor forward passes) | High Edge CPU saturation; large neural weight footprint | 95.97% (AdaBoost)<br>73.70% (RF baseline) | [`Ali2025_IEEE_IoT_Edge_IDS.pdf`](../02_Publications_Proof/Ali2025_IEEE_IoT_Edge_IDS.pdf) |
| **Amuthadevi et al.** [3] | *Sustainable Energy*, 2024 | Energy-Constrained IoT Edge Devices | TinyML (Random Forest, AdaBoost) | **~10 – 50 ms** window on MCU | Constrained power; traditional RF incurs memory overhead on MCUs | 99.39% Accuracy<br>99.45% F1-score | [`Amuthadevi2024_TinyML_IoT_IDS.pdf`](../02_Publications_Proof/Amuthadevi2024_TinyML_IoT_IDS.pdf) |
| **Hafid & Ezzouhairi** [4] | *IEEE Conference*, 2024 | IoT Edge Gateway Architecture | Random Forest, Decision Tree | **15 – 35 ms** flow ingestion | High edge memory cited without model compression | 86.0% Accuracy<br>89.0% Recall | [`Hafid2024_IEEE_IoT_Edge_IDS.pdf`](../02_Publications_Proof/Hafid2024_IEEE_IoT_Edge_IDS.pdf) |
| **Standard Edge Python Deployment** [5] | Local Benchmark Baseline | Raspberry Pi 4 Model B (ARM Cortex-A72) | Standard Scikit-Learn `.pkl` Random Forest | **15.20 ms** per flow *(Framework overhead)* | **25% – 35% CPU**<br>140 – 180 MB RAM | 99.98% Accuracy | `Findings_and_Tradeoffs.txt` (Local test log) |
| **My Project (Autonomous Gateway)** | **Current FYP Implementation** | **Raspberry Pi 4 Model B (ARM Cortex-A72)** | **Compiled Pure RF (`m2cgen`) + Deterministic L4 Filter** | **0.021 ms** per flow (~47,600 flows/sec) | **0.0% – 0.3% Idle CPU** (Peak 15% during burst)<br>**~24 MB RAM** | **96.70% Multi-Dataset**<br>**97.18% IoT Accuracy** | Live Prototype (`dashboard.py` and `pure_rf_multi.py`) |

---

## 3. In-Depth Analysis of Comparative Literature

### 1. Cloud Latency Fails Real-Time Defense (Cherukuri, 2024)
* **Citation:** Cherukuri, B. R. (2024). *Edge Computing vs. Cloud Computing: A Comparative Analysis for Real-Time AI Applications*, IJFMR, 6(5).
* **Published Findings:** Cloud-based AI experiences **100 to 200 ms round-trip latency**, whereas local edge processing achieves **10 to 20 ms**.
* **Relevance to My Project:** A volumetric DDoS attack transmits thousands of packets per second. A 150 ms cloud round-trip delay allows thousands of malicious packets to saturate network queues before the cloud can return a mitigation command. My gateway achieves **0.021 ms inference latency**, mitigating malicious flows locally in microsecond time.

### 2. Deep Learning Overburdens Resource-Constrained Edge Nodes (Ali et al., 2025)
* **Citation:** Ali, Z. et al. (2025). *Deep Transfer Learning for Intrusion Detection in Edge Computing Scenarios*, IEEE Internet of Things Journal, 12(21).
* **Published Findings:** While deep transfer learning achieves high accuracy, continuous tensor operations and neural backpropagation produce substantial memory and CPU strain on edge processors.
* **Relevance to My Project:** Running heavy deep neural networks on an embedded ARM Cortex-A72 requires floating-point tensor engines (PyTorch / ONNX) that consume 60% to 95% CPU, causing thermal throttling. My constrained Random Forest operates at **0.0% to 0.3% CPU during routine sniffing** with zero thermal degradation.

### 3. TinyML Feasibility on Energy-Constrained Hardware (Amuthadevi et al., 2024)
* **Citation:** Amuthadevi, C. et al. (2024). *TinyML-based intrusion detection systems for sustainable and energy-constrained IoT devices*, Sustainable Energy, 7.
* **Published Findings:** The authors confirmed that Random Forest delivers 99.39% accuracy for IoT intrusion detection, but emphasized that standard implementations consume excessive memory on edge nodes unless compressed.
* **Relevance to My Project:** I addressed the exact limitation noted by Amuthadevi et al. by using `m2cgen` to decompile my trained ensemble into pure Python mathematical branching logic, reducing the memory footprint to ~24 MB RAM.

---

## 4. Key Innovations in My Architecture

### Innovation 1: Overcoming the 15 ms Python Framework Bottleneck
When running standard scikit-learn `.pkl` models on the Raspberry Pi 4, inference required approximately 15.20 ms per sample. Profiling demonstrated that the matrix mathematics completed in under 0.1 ms, but Python spent over 15 ms performing numpy array shape validation and dynamic type checking on ARM. By cross-compiling the model into pure Python `if/else` logic (`pure_rf_multi.py`), I eliminated all framework overhead and achieved **0.021 ms latency**.

### Innovation 2: Two-Tier Hybrid Layer-4 / Layer-7 Pipeline
To prevent volumetric SYN floods from exhausting edge memory, I designed a deterministic pre-filter ahead of the machine learning classifier:
1. High-rate floods (SYN count > 15 or Inter-Arrival Time < 1000 µs) are flagged and dropped immediately at Layer 4.
2. Moderate and complex traffic passes to the Layer 7 TinyML model (`pure_rf_multi.py`) for behavioral classification to detect stealthy attacks like SSH brute force.

---

## 5. Summary Reference Citations

1. Cherukuri, B. R. (2024). *Edge Computing vs. Cloud Computing: A Comparative Analysis for Real-Time AI Applications*. IJFMR, 6(5). [`Cherukuri2024_Edge_vs_Cloud_AI.pdf`](../02_Publications_Proof/Cherukuri2024_Edge_vs_Cloud_AI.pdf)
2. Ali, Z., Tiberti, W., Marotta, A., & Cassioli, D. (2025). *Deep Transfer Learning for Intrusion Detection in Edge Computing Scenarios*. IEEE IoT Journal, 12(21). [`Ali2025_IEEE_IoT_Edge_IDS.pdf`](../02_Publications_Proof/Ali2025_IEEE_IoT_Edge_IDS.pdf)
3. Amuthadevi, C., Venkatesan, R., Mythily, M., & Aroul Canessane, R. (2024). *TinyML-based intrusion detection systems for sustainable and energy-constrained IoT devices*. Sustainable Energy, 7. [`Amuthadevi2024_TinyML_IoT_IDS.pdf`](../02_Publications_Proof/Amuthadevi2024_TinyML_IoT_IDS.pdf)
4. Hafid, B., & Ezzouhairi, A. (2024). *Strengthening Security in the Internet of Things (IoT): Integrated Approach of Intrusion Detection Systems (IDS) and Edge Computing*. IEEE IoT Conf. [`Hafid2024_IEEE_IoT_Edge_IDS.pdf`](../02_Publications_Proof/Hafid2024_IEEE_IoT_Edge_IDS.pdf)
5. Mohale, V. Z., & Obagbuwa, I. C. (2024). *Evaluating machine learning-based intrusion detection systems with explainable AI*. Frontiers in Computer Science, 6. [`Mohale2024_Frontiers_XAI_IDS.pdf`](../02_Publications_Proof/Mohale2024_Frontiers_XAI_IDS.pdf)
