# Fraud Detection Subsystem

This project implements a transaction monitoring subsystem designed to detect fraudulent transactions based on rule-based checks and unsupervised machine learning models. Since labeled fraud data is unavailable, this system uses anomaly detection methods to flag suspicious transactions.

---

## Fraud Detection Rules

### Rule A: Standard Deviation-Based Anomaly Detection
**Why?**  
Fraudulent transactions often have unusually high or low amounts compared to a user's normal spending behavior.

**Implementation:**  
A transaction is flagged if it is more than 2.5 standard deviations away from the user's average transaction amount.  
- Threshold: 2.5 SD ensures extreme outliers are captured while minimizing false positives.
- Lower thresholds result in too many false positives.
- Higher thresholds might miss fraudulent activity.

---

### Rule B: High Transaction Volume (Unusual Activity Rule)
**Why?**  
Fraudsters may take control of an account and execute many transactions in a short period.

**Implementation:**  
- If a user’s transaction count is in the top 2% (98th percentile) of all users, their transactions are flagged.
- Fraudulent users often execute bulk transactions to exploit stolen credentials.

---

### Rule C: Large Transactions Relative to User's History
**Why?**  
Fraudsters often execute large transactions to maximize their gain before detection.

**Implementation:**  
- Transactions that are 2.5 standard deviations above the user’s average amount are flagged.
- Ensures user-specific thresholds rather than a fixed transaction limit.

---

### Rule D: High Velocity Transactions
**Why?**  
Fraudsters may execute multiple rapid transactions before the account holder notices.

**Implementation:**  
- If a user executes more than 4 transactions within 5 minutes, they are flagged.
- Captures rapid transaction bursts while avoiding false positives from normal spending behavior.

---

### Rule E: Transactions at Unusual Times
**Why?**  
Fraudulent transactions often occur late at night when users are less likely to notice them.

**Implementation:**  
- Transactions between 12 AM – 4 AM are flagged.
- Studies show fraud attempts increase during off-hours.

---

## Machine Learning-Based Fraud Detection

Since fraudulent transactions do not always follow explicit patterns, unsupervised machine learning is used to detect anomalies.

### Rule F: ML-Based Anomaly Detection (Gaussian Mixture & Isolation Forest)

1. **Gaussian Mixture Model (GMM)**
   - Learns spending patterns dynamically and assigns a likelihood score to transactions.
   - Features used:
     - `amount`
     - `txn_hour`
     - `txn_dow`
     - `amt_to_avg_ratio` (transaction value compared to user's mean spending)
   - Anomalous transactions have low probability scores.
   - Uses `n_components=4` (assuming 4 transaction behavior types).

2. **Isolation Forest**
   - Identifies anomalies in transaction patterns by splitting data recursively.
   - Features used: Same as GMM.
   - Hyperparameters:
     - `n_estimators=100`
     - `contamination=0.005` (assumes 0.5% of transactions are fraudulent).
   - Transactions with low anomaly scores are flagged.

3. **Final Decision:**
   - If both models agree that a transaction is fraudulent, it is flagged.

---

### Rule G: NLP-Based Merchant Name Anomaly Detection
**Why?**  
Fraudulent transactions may involve rare or suspicious merchants.

**Implementation:**
1. **Text Preprocessing:**
   - Merchant names are tokenized using TF-IDF vectorization.
   - Uses character-based n-grams (3-5 chars) to capture misspellings or slight variations.

2. **Merchant Clustering with DBSCAN:**
   - Detects merchant outliers using density-based clustering.
   - `eps=0.4`, `min_samples=4` to ensure distinct clusters.

3. **Isolation Forest on Merchant Embeddings:**
   - Flags merchants significantly different from known merchants.
   - Helps detect small-scale merchant fraud.

**Why is this effective?**
- Prevents fraud through obscure or manipulated merchant names.
- Detects small-scale fraud that traditional rules miss.
- Reduces false positives by ensuring true merchant anomalies.

---

## Why Use Unsupervised Learning?

Traditional supervised machine learning requires labeled fraud data, which is unavailable in this case. Instead, we use unsupervised anomaly detection:

1. **Gaussian Mixture Model (GMM)**
   - Learns statistical clusters of spending behavior.
2. **Isolation Forest**
   - Identifies anomalies in transaction patterns.
3. **DBSCAN (NLP-based merchant analysis)**
   - Clusters merchants based on name similarity to flag fake or unusual merchants.

Together, these models provide a robust fraud detection system capable of identifying suspicious transactions without labeled data.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fraud_detection_subsystem.git
   cd fraud_detection_subsystem
