# fraud_detection_subsystem

**Overview**
This project implements a transaction monitoring subsystem designed to detect fraudulent transactions based on rule-based checks and unsupervised machine learning models. Since labeled fraud data is unavailable, this system uses methods of anomaly detection to flag suspicious transactions

**Rule A: Standard Deviation-Based Anomaly Detection**
  **Why?** Fraudulent transactions often have unusually high or low amounts compared to a user's normal spending behavior.
  **Implementation:** A transaction is flagged if it is more than 2.5 standard deviations away from the user's average transaction amount. The threshold of 2.5 standard deviations is used because it captures extreme outliers while minimizing false positivites. A lower threshold would result in too many false positives, while a higher threshold would be too strict and could potentially miss fraudulent activity.****

**Rule B: High Transaction Voume (Unusual Activity Rule)**
  **Why?** Fraudsters may take control of an account and execute many transactions in a short period. A legitimate user generally follows a consistent transaction pattern, and a sudden spike in activity is suspicious. The top 2% of users (98th percentile) in terms of transaction volume are flagged because fraudulent users often execute bulk transactions within a short period of time.
  **Implementation:** If a user’s transaction count is in the top 2% (98th percentile) of all users, their transactions are flagged.

**Rule C: Large Transactions Relative to User's History**
  **Why?** Fraudsters may execute multiple transactions rapidly to avoid detection. Using a 2.5 SD threshold ensures that we capture significant spikes in spending, specifci to each user's past transactions.
  **Implementation:** Any transaction that is 2.5 SD above the user’s average amount is flagged.

**Rule D: High Velocity Transaction**
  **Why?** Fraudsters may execute multiple transactions rapidly to avoid detection. A standard of 4 or more purchases in 5 minutes captures rapid transaction burts without affecting regular users who make consecutive purchases naturally.
  **Implementation:** If a user executes more than 4 transactions within 5 minutes, it is flagged

**Rule E: Transaction at Unusual Times**
  **Why?** Fraudulent transactions often occur during late-night hours when users are less likely to notice them. Stolen credit cards are often used when the original owner is likely asleep. Studies show that between midnight to 6 AM is when fraud attempts tend to increase (during off-hours), and these hours align with times of lower transaction activity.
  **Implementation:** Transactions between midnight and 4 AM are flagged

**Rule F: ML-Based Anommal Detection (Gaussian Mixture & Isolation Forest)**
**Why?** Fraudulent transactions fo not always follow explicit patterns, so unsupervised ML is used to detect outliers
**Implementation:**
  **1.) Gaussian Mixture Model (GMM):** Identifies transactions that are statistically unusual based on amount, frequency, and time
          **Implementation:** 
          **a.) Feature Selection** - Model is trained on:
                -**account** (transaction value)
                -**txn_hour** (time of transaction)
                -**txn_dow** (day of the week)
                **amt_to_avg_ratio** (ratio of transaction amount to user's mean spending)
          **b.) GMM training** - Model is trained with **n_components = 4** (assuming there are 4 clusters of of transaction behaviors)
          **c.) Anomaly detection** - Transactions with **with low likelihood scores** (computed from GMM) are flagged
          **Why is this effective?**
                - Traditional rules struggle to capture uncommon transaction behaviors, but GMM can learn spending patterns **dynamically**
                - It provides a **continuous probability score**, allowing for **adjustable threshold** instead of hard cutoffs
                
  **2.) Isolation Forest:** Works by randomly splitting transaction features and flags transactions in sparsely populated regions of the dataset based on unusual patterns
          **Implementation:**
          **a.) Feature Selection** - Same feature set as GMM 
              -**amount**
              -**txn_hour**
              -**txn_dow**
              -**amt_to_avg_ratio**
          **b.) Model training** - An Isolation Forest is trained with:
              -**n_estimators = 100** (100 trees)
              -**contamination = 0.005** (assumes 0.5% of transactions are fraudulent)
          **c.) Scoring transactions** - Transactions **with low decision function scores** are flagged as anomalies
          **Why is this effective?**
              - Isolatoin Forest **automatically learns anomalies** from the data
              - It can **detect unknown fraud patterns** without relying on predefined fraud types
              Works **well for datasets with mix** of normal and fraudulent transactions
  **3.)** If both models agree on an anomaly, the transaction is flagged

**Rule G: NLP-Based Merchant Name Anomaly Detection**
  **Why?** Fraudulent transactions may involve merchants rarely used by the cardholder or suspicious merchants. Traditional frad rules don't analyze merchant names, so NLP can add additional fraud detection techniques
  **Implementation:**
    **a.) Text Preprocessing** - Merchant names are tokenized using by **TF-IDF vectorization**
          - Uses character-based n0grams (3-5 characters) to capture **mispellings or slight variations**
    **b.) Clustering with DBSCAN** - Detects **merchant name outliers**
          - **eps = 0.4**, **min_samples = 4** ensures unqiue merchant clusters are detected
    **c.) Isolation Forest on merchant embeddings** - Another Isolation Forest is trained specifically on merchant names
          - This flags merchants that appear significantly **different from known merchants**
    **Why is this effective?**
          - Prevents fraud through obscure merchants or manipulated names
          - Helps detect small-scale merchant fraud, which is hard to detect with **just traditional rules**
          - Reduces **false positives** by ensuring a merchant is truly manual, not just rare

**Why Unsupervised Learning Was Used**
  Fraud detection typically uses **supervised ML**, but this project did not contain labeled fraud data. Instead, we apply **unsupervised learning method:**
  **1.) Gaussian Mixture Model (GMM):** Detects clusters of transactions based on statistical properties
  **2.) Isolation Forest:** Identifies anomalies by recursively partitioning the dataset
  **3.) DBSCAN (NLP-based merchant analysis:** Clusters merchants based on name similarity to identify fake or unusual merchants
  Together, these models help identify outliers amongst the data, which are likely fraudulent transactions
