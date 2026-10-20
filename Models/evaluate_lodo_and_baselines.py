import os
import sys
import zipfile
import time
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from imblearn.over_sampling import SMOTE

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "Datasets")

FEATURES = [
    'Destination Port', 'Bwd Packet Length Std', 'SYN Flag Count', 
    'Flow IAT Mean', 'Total Fwd Packets', 'Flow Duration', 
    'Fwd Packet Length Mean', 'Init_Win_bytes_forward'
]

print("================================================================================")
print(" LEAVE-ONE-DATASET-OUT (LODO) & BASELINE BENCHMARK HARNESS")
print("================================================================================")

# 1. Load CIC-IDS-2017
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
    sampled_2017.append(sub.sample(n=min(len(sub), 20000), random_state=42))
df_2017_clean = pd.concat(sampled_2017, ignore_index=True)
df_2017_clean['Dataset'] = '2017'

# 2. Load CSE-CIC-IDS-2018
df_2018_raw = pd.read_csv(os.path.join(BENCHMARK_DIR, "csecicids2018_sample.csv"))
df_2018_clean = pd.DataFrame()
df_2018_clean['Destination Port'] = df_2018_raw['Dst Port']
df_2018_clean['Bwd Packet Length Std'] = df_2018_raw['Bwd Pkt Len Std']
df_2018_clean['SYN Flag Count'] = df_2018_raw['SYN Flag Cnt']
df_2018_clean['Flow IAT Mean'] = df_2018_raw['Flow IAT Mean']
df_2018_clean['Total Fwd Packets'] = df_2018_raw['Tot Fwd Pkts']
df_2018_clean['Flow Duration'] = df_2018_raw['Flow Duration']
df_2018_clean['Fwd Packet Length Mean'] = df_2018_raw['Fwd Pkt Len Mean']
df_2018_clean['Init_Win_bytes_forward'] = df_2018_raw['Init Fwd Win Byts']

def map_2018(l):
    if 'benign' in str(l).lower(): return 'BENIGN'
    if any(k in str(l).lower() for k in ['ddos', 'dos']): return 'DDoS'
    if any(k in str(l).lower() for k in ['bruteforce', 'brute force']): return 'SSH-Patator'
    return None

df_2018_clean['Label'] = df_2018_raw['Label'].apply(map_2018)
df_2018_clean = df_2018_clean.dropna(subset=FEATURES + ['Label']).copy()
df_2018_clean['Dataset'] = '2018'

# 3. Load CIC-DDoS-2019
df_2019_raw = pd.read_csv(os.path.join(BENCHMARK_DIR, "cicddos2019_syn_sample.csv"), low_memory=False)
df_2019_raw.columns = df_2019_raw.columns.str.strip()
df_2019_clean = pd.DataFrame()
for f in FEATURES:
    df_2019_clean[f] = df_2019_raw[f]

df_2019_clean['Label'] = df_2019_raw['Label'].apply(
    lambda l: 'DDoS' if 'syn' in str(l).lower() else ('BENIGN' if 'benign' in str(l).lower() else None)
)
df_2019_clean = df_2019_clean.dropna(subset=FEATURES + ['Label']).copy()
df_2019_clean = df_2019_clean.sample(n=min(len(df_2019_clean), 20000), random_state=42)
df_2019_clean['Dataset'] = '2019'

datasets = {'2017': df_2017_clean, '2018': df_2018_clean, '2019': df_2019_clean}

for name, df in datasets.items():
    print(f"Dataset {name}: {len(df)} flows | Distribution: {dict(df['Label'].value_counts())}")

print("\n--------------------------------------------------------------------------------")
print(" PART 1: LEAVE-ONE-DATASET-OUT (LODO) GENERALIZATION EXPERIMENTS")
print("--------------------------------------------------------------------------------")

lodo_results = []
for test_ds in ['2018', '2019', '2017']:
    train_datasets = [d for d in datasets.keys() if d != test_ds]
    df_train = pd.concat([datasets[d] for d in train_datasets], ignore_index=True)
    df_test = datasets[test_ds].copy()

    df_train.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_train.dropna(subset=FEATURES + ['Label'], inplace=True)
    df_test.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_test.dropna(subset=FEATURES + ['Label'], inplace=True)

    X_train = df_train[FEATURES]
    y_train = df_train['Label']
    X_test = df_test[FEATURES]
    y_test = df_test['Label']

    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=25, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train_res, y_train_res)
    y_pred = rf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    
    # Calculate False Positive Rate (FPR) on Benign
    cm = confusion_matrix(y_test, y_pred, labels=['BENIGN', 'DDoS', 'SSH-Patator'])
    benign_total = cm[0].sum()
    benign_fp = cm[0, 1] + cm[0, 2]
    fpr = (benign_fp / benign_total * 100) if benign_total > 0 else 0.0

    print(f"Train on {train_datasets} -> Test on {test_ds} (Unseen Domain):")
    print(f"  Accuracy: {acc*100:.2f}% | Macro F1: {f1:.4f} | Benign FPR: {fpr:.2f}%")
    print(f"  Confusion Matrix (Row=Actual, Col=Pred [BENIGN, DDoS, SSH]):")
    print(f"  {cm[0]}\n  {cm[1]}\n  {cm[2] if len(cm) > 2 else ''}\n")

    lodo_results.append({
        'Test_Dataset': test_ds,
        'Train_Datasets': "+".join(train_datasets),
        'Accuracy': acc * 100,
        'Macro_F1': f1,
        'Benign_FPR': fpr,
        'Test_Flows': len(y_test)
    })

print("--------------------------------------------------------------------------------")
print(" PART 2: BASELINE COMPARISON ON UNIFIED CORPUS")
print("--------------------------------------------------------------------------------")

df_all = pd.concat([df_2017_clean, df_2018_clean, df_2019_clean], ignore_index=True)
df_all.replace([np.inf, -np.inf], np.nan, inplace=True)
df_all.dropna(subset=FEATURES + ['Label'], inplace=True)

from sklearn.model_selection import train_test_split
X = df_all[FEATURES]
y = df_all['Label']
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

smote = SMOTE(random_state=42)
X_tr_sm, y_tr_sm = smote.fit_resample(X_tr, y_tr)

# 1. Baseline: Static Heuristic Rules (Fail2ban/Rate-Limiter analogy)
def heuristic_predict(row):
    dport = row['Destination Port']
    syn = row['SYN Flag Count']
    iat = row['Flow IAT Mean']
    if syn >= 5 or (iat > 0 and iat < 500):
        return 'DDoS'
    if dport == 22:
        return 'SSH-Patator'
    return 'BENIGN'

t0 = time.perf_counter()
y_pred_heur = [heuristic_predict(row) for _, row in X_te.iterrows()]
lat_heur = (time.perf_counter() - t0) / len(X_te) * 1000
acc_heur = accuracy_score(y_te, y_pred_heur)
p_h, r_h, f1_heur, _ = precision_recall_fscore_support(y_te, y_pred_heur, average='macro', zero_division=0)
cm_h = confusion_matrix(y_te, y_pred_heur, labels=['BENIGN', 'DDoS', 'SSH-Patator'])
fpr_heur = ((cm_h[0, 1] + cm_h[0, 2]) / cm_h[0].sum()) * 100

# 2. Baseline: Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_tr_sm, y_tr_sm)
t0 = time.perf_counter()
y_pred_lr = lr.predict(X_te)
lat_lr = (time.perf_counter() - t0) / len(X_te) * 1000
acc_lr = accuracy_score(y_te, y_pred_lr)
p_l, r_l, f1_lr, _ = precision_recall_fscore_support(y_te, y_pred_lr, average='macro', zero_division=0)
cm_lr = confusion_matrix(y_te, y_pred_lr, labels=['BENIGN', 'DDoS', 'SSH-Patator'])
fpr_lr = ((cm_lr[0, 1] + cm_lr[0, 2]) / cm_lr[0].sum()) * 100

# 3. Baseline: Single Shallow Decision Tree (depth=5)
dt = DecisionTreeClassifier(max_depth=5, random_state=42)
dt.fit(X_tr_sm, y_tr_sm)
t0 = time.perf_counter()
y_pred_dt = dt.predict(X_te)
lat_dt = (time.perf_counter() - t0) / len(X_te) * 1000
acc_dt = accuracy_score(y_te, y_pred_dt)
p_d, r_d, f1_dt, _ = precision_recall_fscore_support(y_te, y_pred_dt, average='macro', zero_division=0)
cm_dt = confusion_matrix(y_te, y_pred_dt, labels=['BENIGN', 'DDoS', 'SSH-Patator'])
fpr_dt = ((cm_dt[0, 1] + cm_dt[0, 2]) / cm_dt[0].sum()) * 100

# 4. Proposed: Constrained Random Forest (depth=12, n=25)
rf = RandomForestClassifier(n_estimators=25, max_depth=12, random_state=42, n_jobs=-1)
rf.fit(X_tr_sm, y_tr_sm)
t0 = time.perf_counter()
y_pred_rf = rf.predict(X_te)
lat_rf = (time.perf_counter() - t0) / len(X_te) * 1000
acc_rf = accuracy_score(y_te, y_pred_rf)
p_r, r_r, f1_rf, _ = precision_recall_fscore_support(y_te, y_pred_rf, average='macro', zero_division=0)
cm_rf = confusion_matrix(y_te, y_pred_rf, labels=['BENIGN', 'DDoS', 'SSH-Patator'])
fpr_rf = ((cm_rf[0, 1] + cm_rf[0, 2]) / cm_rf[0].sum()) * 100

print(f"{'Model Architecture':<30} | {'Accuracy':<10} | {'Macro F1':<10} | {'Benign FPR':<10} | {'Inference Latency':<15}")
print("-" * 85)
print(f"{'1. Static Heuristic Threshold':<30} | {acc_heur*100:<9.2f}% | {f1_heur:<10.4f} | {fpr_heur:<9.2f}% | {lat_heur:<13.4f} ms")
print(f"{'2. Logistic Regression (L2)':<30} | {acc_lr*100:<9.2f}% | {f1_lr:<10.4f} | {fpr_lr:<9.2f}% | {lat_lr:<13.4f} ms")
print(f"{'3. Single Decision Tree (d=5)':<30} | {acc_dt*100:<9.2f}% | {f1_dt:<10.4f} | {fpr_dt:<9.2f}% | {lat_dt:<13.4f} ms")
print(f"{'4. Proposed Random Forest (d=12)':<30} | {acc_rf*100:<9.2f}% | {f1_rf:<10.4f} | {fpr_rf:<9.2f}% | {lat_rf:<13.4f} ms")

report_path = os.path.join(PROJECT_ROOT, "Documentation", "history", "history_lodo_and_baselines.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("EMPIRICAL BENCHMARK: LEAVE-ONE-DATASET-OUT (LODO) AND BASELINE COMPARISONS\n\n")
    f.write("1. LEAVE-ONE-DATASET-OUT (LODO) EXPERIMENTAL RESULTS\n")
    f.write(pd.DataFrame(lodo_results).to_string(index=False))
    f.write("\n\n2. MODEL ARCHITECTURE BASELINE COMPARISONS\n")
    f.write(f"{'Model':<30} | {'Accuracy':<10} | {'Macro F1':<10} | {'Benign FPR':<10} | {'Latency':<15}\n")
    f.write(f"{'1. Static Heuristic Rule':<30} | {acc_heur*100:<9.2f}% | {f1_heur:<10.4f} | {fpr_heur:<9.2f}% | {lat_heur:<13.4f} ms\n")
    f.write(f"{'2. Logistic Regression':<30} | {acc_lr*100:<9.2f}% | {f1_lr:<10.4f} | {fpr_lr:<9.2f}% | {lat_lr:<13.4f} ms\n")
    f.write(f"{'3. Single Decision Tree':<30} | {acc_dt*100:<9.2f}% | {f1_dt:<10.4f} | {fpr_dt:<9.2f}% | {lat_dt:<13.4f} ms\n")
    f.write(f"{'4. Proposed Random Forest':<30} | {acc_rf*100:<9.2f}% | {f1_rf:<10.4f} | {fpr_rf:<9.2f}% | {lat_rf:<13.4f} ms\n")
print(f"\n[+] Results written to {report_path}")
