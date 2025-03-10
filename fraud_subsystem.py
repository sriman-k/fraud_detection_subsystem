import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.mixture import GaussianMixture
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Parse command-line arguments for the transactions file
parser = argparse.ArgumentParser(description="Fraud Detection Script")
parser.add_argument("transactions_file", type=str, help="Path to the transactions CSV file")
args = parser.parse_args()

# Load transactions dataset from the provided file path
txn_df = pd.read_csv(args.transactions_file, parse_dates=['timestamp'])

# Load MCC dataset from the file "mcc_codes.csv" (assumed to be in the same directory)
mcc_file = "mcc_codes.csv"
mcc_df = pd.read_csv(mcc_file)

# Normalize column names to lowercase
mcc_df.columns = mcc_df.columns.str.lower()

# Create MCC dictionary (adjust column names as needed)
mcc_dict = dict(zip(mcc_df['mcc'], mcc_df['combined_description']))

# --- MCC VALIDATION ---
def validate_merchant_mcc(row):
    mcc = row.get('merchant_mcc', None)
    name = row['merchant_name'].lower()
    if mcc in mcc_dict:
        category = mcc_dict[mcc].lower()
        return any(word in name for word in category.split())
    return False

txn_df['mcc_valid'] = txn_df.apply(validate_merchant_mcc, axis=1)

# --- FEATURE ENGINEERING ---
txn_df['txn_hour'] = txn_df['timestamp'].dt.hour
txn_df['txn_dow'] = txn_df['timestamp'].dt.dayofweek
txn_df['amt_to_avg_ratio'] = txn_df['amount'] / txn_df.groupby('user_id')['amount'].transform('mean')

# Rule A: Standard deviation-based anomaly detection
txn_df['amt_std'] = txn_df.groupby('user_id')['amount'].transform('std')
txn_df['amt_mean'] = txn_df.groupby('user_id')['amount'].transform('mean')
txn_df['amt_z_score'] = (txn_df['amount'] - txn_df['amt_mean']) / txn_df['amt_std']
txn_df['rule_std_dev'] = txn_df['amt_z_score'].abs() > 2.5  

# Rule B: Unusually high transaction volume
txn_df['user_txn_count'] = txn_df.groupby('user_id')['timestamp'].transform('count')
txn_df['rule_unusual_activity'] = txn_df['user_txn_count'] > txn_df['user_txn_count'].quantile(0.98)

# --- UNSUPERVISED LEARNING ---
features = ['amount', 'txn_hour', 'txn_dow', 'amt_to_avg_ratio']
X = txn_df[features].fillna(0)

# GMM Anomaly Detection
gmm = GaussianMixture(n_components=4, covariance_type='full', random_state=42)
gmm.fit(X)
txn_df['gmm_score'] = -gmm.score_samples(X)

# Isolation Forest Anomaly Detection
iso = IsolationForest(n_estimators=100, contamination=0.005, random_state=42)
iso.fit(X)
txn_df['iso_score'] = -iso.decision_function(X)
txn_df['iso_anomaly'] = iso.predict(X)  # -1 indicates an anomaly

# --- RULE-BASED FRAUD DETECTION ---
# Rule C: Large transactions relative to user spending pattern
txn_df['rule_large'] = txn_df['amount'] > (txn_df['amt_mean'] + 2.5 * txn_df['amt_std'])

# Rule D: High transaction velocity (sorted by timestamp for accuracy)
txn_df = txn_df.sort_values(['user_id', 'timestamp'])
txn_df['prev_txn_time'] = txn_df.groupby('user_id')['timestamp'].shift(1)
txn_df['time_since_prev'] = (txn_df['timestamp'] - txn_df['prev_txn_time']).dt.total_seconds()
txn_df['recent_txn_count'] = txn_df.groupby('user_id')['timestamp'].diff().lt(pd.Timedelta(seconds=300)).astype(int).groupby(txn_df['user_id']).cumsum()
txn_df['rule_velocity'] = txn_df['recent_txn_count'] > 4

# Rule E: Transactions at unusual times (e.g., early morning hours)
txn_df['rule_time'] = txn_df['txn_hour'].isin([0, 1, 2, 3, 4])

# Rule F: ML-based anomaly detection using Isolation Forest
txn_df['rule_ml_anomaly'] = txn_df['iso_anomaly'] == -1

# Rule G: Detecting rare merchant activity
txn_df['small_txn'] = txn_df['amount'] < 5
txn_df['small_streak'] = txn_df.groupby('user_id')['small_txn'].transform(
    lambda x: x.groupby((x != x.shift()).cumsum()).cumsum()
)
txn_df['rule_structuring'] = txn_df['small_streak'] >= 2

merchant_counts = txn_df['merchant_name'].value_counts()
threshold = merchant_counts.quantile(0.05)
rare_merchants = set(merchant_counts[merchant_counts <= threshold].index)
txn_df['rule_deviation'] = txn_df['merchant_name'].isin(rare_merchants) & (txn_df['amount'] > txn_df['amount'].quantile(0.85))

# --- FINAL FRAUD FLAGGING ---
txn_df['fraud_risk_score'] = txn_df[['gmm_score', 'iso_score']].sum(axis=1)
# Assuming an 'is_fraud' column exists in your dataset for reference
fraud_threshold = txn_df[txn_df['is_fraud'] == True]['fraud_risk_score'].quantile(0.85)
txn_df['is_fraud_flagged'] = (
    (txn_df[['rule_large', 'rule_std_dev', 'rule_velocity', 'rule_time', 'rule_deviation', 'rule_unusual_activity', 'rule_ml_anomaly']].sum(axis=1) > 3) | 
    ((txn_df['fraud_risk_score'] > fraud_threshold) & (txn_df['iso_anomaly'] == -1))
)

# Save flagged transactions to a CSV file
flagged_transactions = txn_df[txn_df['is_fraud_flagged']]
flagged_transactions.to_csv("flagged_transactions.csv", index=False)

print("Flagged transactions saved to 'flagged_transactions.csv'")
