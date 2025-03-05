# Fraud Detection Subsystem

This project implements a transaction monitoring subsystem designed to detect fraudulent transactions using rule-based checks and unsupervised machine learning models. In the absence of labeled fraud data, the system employs anomaly detection methods to flag suspicious transactions.

---

## Fraud Detection Rules

### Rule A: Standard Deviation-Based Anomaly Detection

**Why?**  
Fraudulent transactions often exhibit amounts significantly higher or lower than a user's typical spending behavior. According to the Ohio State University report on fraud detection, standard deviation-based anomaly detection is widely used for identifying outliers in financial transactions.

**Implementation:**  
A transaction is flagged if it deviates more than 2.5 standard deviations from the user's average transaction amount. This threshold effectively captures outliers while minimizing false positives.

**Source:**  
https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/3/40936/files/2016/12/stats_for_fraud-10cf3pc.pdf

---

### Rule B: High Transaction Volume (Unusual Activity Rule)

**Why?**  
A sudden spike in the number of transactions within a short period may indicate fraudulent activity, as fraudsters often attempt multiple transactions rapidly. The U.S. Payments Forum discusses how velocity checks are effective in flagging excessive transaction activity within a short window.

**Implementation:**  
Transactions are flagged if a user's transaction count falls within the top 2% (98th percentile) of all users.

**Source:**  
https://www.uspaymentsforum.org/wp-content/uploads/2021/08/Velocity-Checks.pdf

---

### Rule C: Large Transactions Relative to User's History

**Why?**  
Transactions significantly larger than a user's typical spending may signal fraudulent activity. The Ohio State University report highlights how standard deviation techniques are used to detect deviations in transaction amounts that indicate fraud.

**Implementation:**  
Any transaction exceeding 2.5 standard deviations above the user’s average amount is flagged.

**Source:**  
https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/3/40936/files/2016/12/stats_for_fraud-10cf3pc.pdf

---

### Rule D: High Velocity Transactions

**Why?**  
Multiple rapid transactions within a short timeframe can indicate fraudulent behavior, as fraudsters may attempt numerous transactions before detection. Chargebacks911 explains how velocity checks help in identifying rapid bursts of transactions, which often signal fraudulent card activity.

**Implementation:**  
If a user performs more than four transactions within five minutes, those transactions are flagged.

**Source:**  
https://chargebacks911.com/velocity-checks/

---

### Rule E: Transactions at Unusual Times

**Why?**  
Transactions occurring during atypical hours, such as late at night, may suggest fraudulent activity, as fraudsters often operate when account holders are less likely to notice. HighRadius highlights that fraud attempts tend to peak during non-business hours, particularly late at night.

**Implementation:**  
Transactions between 12 AM and 4 AM are flagged.

**Source:**  
https://www.highradius.com/resources/Blog/transaction-data-anomaly-detection/

---

## Machine Learning-Based Fraud Detection

In addition to rule-based methods, unsupervised machine learning models are employed to detect anomalies that may indicate fraud.

### Rule F: ML-Based Anomaly Detection (Gaussian Mixture & Isolation Forest)

1. **Gaussian Mixture Model (GMM)**
   - **Why?**  
     GMMs can identify patterns in transaction data, allowing for the detection of anomalies that deviate from typical behavior. According to Fraud.com, machine learning-based anomaly detection is a key technique in modern fraud prevention.
   - **Implementation:**  
     Features such as transaction amount, time, day of the week, and the ratio of transaction amount to the user's average spending are used to train the model. Transactions with low probability scores are flagged as anomalies.

2. **Isolation Forest**
   - **Why?**  
     Isolation Forests are effective in detecting anomalies by isolating observations in the data, making them suitable for identifying fraudulent transactions. Fraud.com further explains that Isolation Forest models are widely used due to their efficiency in unsupervised fraud detection.
   - **Implementation:**  
     The model is trained using features similar to those in the GMM. Transactions with low anomaly scores are flagged.

**Source:**  
https://www.fraud.com/post/anomaly-detection

---

### Rule G: NLP-Based Merchant Name Anomaly Detection

**Why?**  
Fraudulent transactions may involve merchants that are unusual or unfamiliar to the user. Fraud.com discusses how merchant-based anomaly detection using NLP techniques can help identify suspicious transactions linked to fraudulent merchants.

**Implementation:**  
Natural Language Processing (NLP) techniques, such as TF-IDF vectorization and clustering algorithms like DBSCAN, are used to analyze merchant names. This helps detect anomalies in merchant names that could indicate fraudulent activity.

**Source:**  
https://www.fraud.com/post/anomaly-detection

---

## Why Use Unsupervised Learning?

In the absence of labeled fraud data, unsupervised learning methods are effective in detecting anomalies that may indicate fraudulent activity. Fraud.com explains that anomaly detection methods such as Isolation Forest and Gaussian Mixture Models help businesses detect fraud without the need for labeled data.

**Source:**  
https://www.fraud.com/post/anomaly-detection

---

## Pros & Cons

### **Pros**
- **Uses both rule-based and ML-based approaches**  
  - The five rules help capture common fraud patterns, while ML-based models detect subtle fraud behavior.
- **Unsupervised learning allows fraud detection without labeled data**  
  - Since labeled fraud data is unavailable, using a GMM and Isolation Forest helped identify anomalies without requiring predefined fraudulent examples.
- **Industry-backed fraud detection rules**  
  - Though simple and straightforward, the rules capture many commonly committed fraudulent behaviors, backed by research and used by banks and credit card companies.
- **Ensuring fair strictness standard and false positives**  
  - Implementing a 2.5 standard deviation for transaction amounts minimizes false positives while still identifying outliers.

### **Cons**
- **No access to location data**  
  - Initially, I thought using transaction location would be a perfect feature to detect fraud. Many fraud systems use geolocation checks, but this was unavailable.
- **Threshold tuning is arbitrary**  
  - Some thresholds (e.g., 98th percentile for high transaction volume) were chosen based on heuristics rather than actual validation. Ideally, these would be fine-tuned using real fraud datasets.
- **Rule-based methods may not generalize well**  
  - As fraud patterns change quickly, rule-based identification may become outdated without continuous updating.

---

## If Given More Time

- **Train a supervised model on real fraud data**  
  - With labeled fraud transaction data, I would train a Random Forest model to predict fraud probability instead of relying solely on unsupervised ML.
- **Use real-time data**  
  - Implement fraud detection as transactions occur instead of batch processing CSVs.
- **Incorporate additional features**  
  - Features like IP addresses and login patterns would significantly improve accuracy.
- **Add explanations for flagged transactions**  
  - A frontend feature displaying reasons for flagged transactions would help fraud analysts understand cases.

---

## My Approach

1. **Started with basic rule-based fraud detection**  
   - Identified common rules like velocity checks, transaction amount outliers, and transactions at unusual timings.
2. **Realized rule-based methods alone are insufficient**  
   - Static rules are too rigid to detect evolving fraud patterns.
3. **Researched fraud detection on unlabeled datasets**  
   - Found that unsupervised learning could dynamically capture anomalies.
4. **Decided on Gaussian Mixture Models (GMM)**  
   - GMM clusters normal vs. abnormal spending behaviors to detect outliers.
5. **Added Isolation Forest**  
   - Isolation Forest is widely used in fraud detection to identify anomalies without labeled fraud data.
6. **Incorporated NLP-based merchant analysis**  
   - Thought about how slight misspellings in merchant names could indicate fraud, leading to the use of NLP techniques.
7. **Finalized the combined rule-based and ML approach**  
   - Balancing strict rule-based detection with flexible ML-based anomaly detection.

---
