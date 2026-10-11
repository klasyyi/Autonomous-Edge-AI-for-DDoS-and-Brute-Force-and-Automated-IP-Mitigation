import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import m2cgen as m2c
import zipfile

print("Loading Friday (DDoS) dataset...")
df_friday = pd.read_csv("Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")

print("Loading Tuesday (SSH) dataset from zip...")
zf = zipfile.ZipFile('MachineLearningCSV.zip')
df_tuesday = pd.read_csv(zf.open('MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv'))

print("Combining datasets...")
df = pd.concat([df_friday, df_tuesday], ignore_index=True)

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)
df.columns = df.columns.str.strip()

features = [
    'Destination Port', 'Bwd Packet Length Std', 'SYN Flag Count', 
    'Flow IAT Mean', 'Total Fwd Packets', 'Flow Duration', 
    'Fwd Packet Length Mean', 'Init_Win_bytes_forward'
]

df = df[df['Label'].isin(['BENIGN', 'DDoS', 'SSH-Patator'])]

X = df[features]
y = df['Label']

print("Value counts before balancing:")
print(y.value_counts())

print("Splitting and applying SMOTE...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_df = X_train.copy()
train_df['Label'] = y_train
sampled_dfs = []
for label in train_df['Label'].unique():
    subset = train_df[train_df['Label'] == label]
    if len(subset) > 50000:
        subset = subset.sample(n=50000, random_state=42)
    sampled_dfs.append(subset)
train_df = pd.concat(sampled_dfs)

X_train_sub = train_df[features]
y_train_sub = train_df['Label']

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train_sub, y_train_sub)

print("Training V2 Model (3 Classes)...")
rf_model = RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train_smote, y_train_smote)

print("Model Classes:", rf_model.classes_)

print("Exporting to pure Python...")
code = m2c.export_to_python(rf_model)
with open("pure_rf_v2.py", "w") as f:
    f.write(code)

print("Done! Saved as pure_rf_v2.py")
