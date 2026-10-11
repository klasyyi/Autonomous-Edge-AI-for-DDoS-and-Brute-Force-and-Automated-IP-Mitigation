import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import zipfile
import m2cgen as m2c
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FEATURES = [
    'Destination Port', 'Bwd Packet Length Std', 'SYN Flag Count', 
    'Flow IAT Mean', 'Total Fwd Packets', 'Flow Duration', 
    'Fwd Packet Length Mean', 'Init_Win_bytes_forward'
]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "04_Dataset_Benchmarks")
if not os.path.exists(BENCHMARK_DIR):
    BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "multi_dataset_benchmark")

print("Universal Multi-Dataset TinyML Training")
print("Datasets: CIC-IDS-2017, CSE-CIC-IDS2018, CIC-DDoS2019")

path_2017_friday = r"C:\Users\syara\OneDrive\Desktop\Final_Year_Final_Sem\FYP1\Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
path_2017_zip = r"C:\Users\syara\OneDrive\Desktop\Final_Year_Final_Sem\FYP1\MachineLearningCSV.zip"

df_friday = pd.read_csv(path_2017_friday)
zf = zipfile.ZipFile(path_2017_zip)
df_tuesday = pd.read_csv(zf.open('MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv'))
df_2017 = pd.concat([df_friday, df_tuesday], ignore_index=True)
df_2017.columns = df_2017.columns.str.strip()
df_2017 = df_2017[df_2017['Label'].isin(['BENIGN', 'DDoS', 'SSH-Patator'])][FEATURES + ['Label']].copy()

sampled_2017 = []
for lbl in ['BENIGN', 'DDoS', 'SSH-Patator']:
    sub = df_2017[df_2017['Label'] == lbl]
    sampled_2017.append(sub.sample(n=min(len(sub), 25000), random_state=42))
df_2017_sub = pd.concat(sampled_2017)
df_2017_sub['Source_Dataset'] = 'CIC-IDS-2017'

df_2018_raw = pd.read_csv(os.path.join(BENCHMARK_DIR, "csecicids2018_sample.csv"))
df_2018 = pd.DataFrame()
df_2018['Destination Port'] = df_2018_raw['Dst Port']
df_2018['Bwd Packet Length Std'] = df_2018_raw['Bwd Pkt Len Std']
df_2018['SYN Flag Count'] = df_2018_raw['SYN Flag Cnt']
df_2018['Flow IAT Mean'] = df_2018_raw['Flow IAT Mean']
df_2018['Total Fwd Packets'] = df_2018_raw['Tot Fwd Pkts']
df_2018['Flow Duration'] = df_2018_raw['Flow Duration']
df_2018['Fwd Packet Length Mean'] = df_2018_raw['Fwd Pkt Len Mean']
df_2018['Init_Win_bytes_forward'] = df_2018_raw['Init Fwd Win Byts']

def map_2018(l):
    if 'benign' in str(l).lower(): return 'BENIGN'
    if any(k in str(l).lower() for k in ['ddos', 'dos']): return 'DDoS'
    if any(k in str(l).lower() for k in ['bruteforce', 'brute force']): return 'SSH-Patator'
    return None

df_2018['Label'] = df_2018_raw['Label'].apply(map_2018)
df_2018 = df_2018.dropna(subset=FEATURES + ['Label']).copy()
df_2018['Source_Dataset'] = 'CSE-CIC-IDS2018'

df_2019_raw = pd.read_csv(os.path.join(BENCHMARK_DIR, "cicddos2019_syn_sample.csv"), low_memory=False)
df_2019_raw.columns = df_2019_raw.columns.str.strip()
df_2019 = pd.DataFrame()
for f in FEATURES:
    df_2019[f] = df_2019_raw[f]

df_2019['Label'] = df_2019_raw['Label'].apply(lambda l: 'DDoS' if 'syn' in str(l).lower() else ('BENIGN' if 'benign' in str(l).lower() else None))
df_2019 = df_2019.dropna(subset=FEATURES + ['Label']).copy()
df_2019 = df_2019.sample(n=min(len(df_2019), 25000), random_state=42)
df_2019['Source_Dataset'] = 'CIC-DDoS2019'

df_all = pd.concat([df_2017_sub, df_2018, df_2019], ignore_index=True)
df_all.replace([np.inf, -np.inf], np.nan, inplace=True)
df_all.dropna(subset=FEATURES + ['Label'], inplace=True)

X = df_all[FEATURES]
y = df_all['Label']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

rf_multi = RandomForestClassifier(n_estimators=25, max_depth=12, random_state=42, n_jobs=-1)
rf_multi.fit(X_train_smote, y_train_smote)

y_pred = rf_multi.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"Overall Accuracy: {acc * 100:.2f}%")
report_str = classification_report(y_test, y_pred, digits=4)
print(report_str)

report_dest = os.path.join(PROJECT_ROOT, "01_Documentation_and_Viva", "multi_dataset_evaluation_report.txt")
with open(report_dest, "w") as f:
    f.write("UNIVERSAL MULTI-DATASET MODEL EVALUATION (2017 + 2018 + 2019)\n")
    f.write(f"Overall Accuracy: {acc * 100:.2f}%\n\n")
    f.write(report_str)

code = m2c.export_to_python(rf_multi)

model_dest_1 = os.path.join(SCRIPT_DIR, "pure_rf_multi.py")
with open(model_dest_1, "w") as f:
    f.write(code)

model_dest_2 = os.path.join(PROJECT_ROOT, "05_Gateway_Runtime", "pure_rf_multi.py")
with open(model_dest_2, "w") as f:
    f.write(code)
