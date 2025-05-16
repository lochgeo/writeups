## **Hackathon Problem Statement: Build a Fraud Profile for Internet Banking Users**

### **Background:**

In the world of digital banking, fraud prevention requires understanding not only *who* the user is but also *how* they behave. Most anomaly detection systems hinge on having a solid baseline of typical user behavior — a **fraud profile**.

A fraud profile captures both **identity signals** (devices, IPs, login times) and **behavioral patterns** (features used, transaction types, timing, and navigation flows). It serves as a digital fingerprint that evolves over time, enabling real-time detection of abnormal activities such as account takeovers, social engineering exploits, or unauthorized access.

---

### **Problem Statement:**

**Build a dynamic fraud profile engine for internet banking users** that captures and summarizes each user's typical access, device, feature usage, and transaction behaviors.

Your task is to process historical login, navigation, and transaction logs to construct a per-user fraud profile. This profile will later serve as the baseline for anomaly detection.

---

### **Data Provided:**

You will receive simulated or anonymized datasets containing the following event types:

* **Login metadata:** user ID, timestamp, device type, OS/browser, screen resolution, IP/geolocation, login method, channel
* **Session metadata:** session duration, pages/screens visited
* **Transaction metadata:** transaction type, amount, recipient, method, timestamp
* **Feature usage logs:** feature name, frequency, timestamps
* (Optional) Derived risk indicators: e.g., failed logins, new device flags, geo-distance between logins

---

### **What You Need to Build:**

#### ✅ **Fraud Profile Generator**

For each user, construct a fraud profile with the following key sections:

1. **Access Profile:**

   * Common login times (hour of day, day of week)
   * Frequently used devices, operating systems, screen resolutions
   * Typical login locations (IP ranges, geolocations)
   * Login methods (OTP, password, biometric)
   * Preferred channels (web, mobile app)
   * Session duration norms

2. **Feature Usage Profile:**

   * Most and least used banking features
   * Typical feature access sequence
   * Frequency and timing of feature usage
   * Features never accessed (anomalous if suddenly used)

3. **Transactional Behavior Profile:**

   * Common transaction types (e.g., NEFT, UPI, bill pay)
   * Average, median, and variance in transaction amounts
   * Frequent payees and destinations
   * Usual transaction times and days
   * Domestic vs. international activity

4. **Optional Enhancements:**

   * Risk scoring system based on profile deviation
   * Visualization dashboard for fraud profiles
   * Alert generator for anomalous activities
   * Behavioral clustering to identify outlier users

---

### **Expected Outcomes:**

* A dynamic, structured fraud profile per user
* Capability to update the profile with new login and transaction events
* A sample API or visualization for querying/viewing a user’s fraud profile
* A basic anomaly detection component (bonus) that flags unusual events

---

### **Benefits of Building This in a Bank:**

* **Foundation for Advanced Fraud Detection:** Enables behavior-based anomaly alerts.
* **Reduces False Positives:** By understanding normal usage patterns.
* **Improves Customer Trust:** By detecting and preventing account compromise faster.
* **Enhances Data Reusability:** Fraud profiles can feed into risk engines, authentication decisions, and transaction monitoring.
* **Cross-Channel Security:** Bridges behavior across mobile, web, and other banking interfaces.

---

### **Judging Criteria:**

* **Completeness:** Does the profile cover all relevant dimensions (access, behavior, transaction)?
* **Scalability:** Can the solution handle 100k+ users and evolving data?
* **Innovation:** Any novel behavioral modeling, feature engineering, or clustering?
* **Real-world Applicability:** Can the fraud profile integrate into existing fraud detection platforms?
* **Explainability:** Can it explain *why* an activity is anomalous?

