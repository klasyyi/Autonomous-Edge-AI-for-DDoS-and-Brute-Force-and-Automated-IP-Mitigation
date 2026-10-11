import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import zipfile

print("1. Loading original datasets...")
df_friday = pd.read_csv("../../FYP1/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")
zf = zipfile.ZipFile('../../FYP1/MachineLearningCSV.zip')
df_tuesday = pd.read_csv(zf.open('MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv'))

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

print("2. Splitting data into 80% Training and 20% Unseen Testing...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("3. Applying SMOTE to balance the 80% Training Data...")
train_df = X_train.copy()
train_df['Label'] = y_train
sampled_dfs = []
for label in train_df['Label'].unique():
    subset = train_df[train_df['Label'] == label]
    if len(subset) > 50000:
        subset = subset.sample(n=50000, random_state=42)
    sampled_dfs.append(subset)
train_df = pd.concat(sampled_dfs)

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(train_df[features], train_df['Label'])

print("4. Training the Random Forest Model...")
rf_model = RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train_smote, y_train_smote)

print("5. Evaluating model strictly against the 20% Unseen Testing Data...")
y_pred = rf_model.predict(X_test)

print("\n================ RESULTS ================")
print(f"Overall Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))
print("=========================================")
