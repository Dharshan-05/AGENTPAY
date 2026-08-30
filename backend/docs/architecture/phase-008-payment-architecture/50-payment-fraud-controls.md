# AGENTPAY — 50: Real-Time Fraud Prevention & Anomaly Detection

## 1. Real-Time Fraud Controls

* **Velocity Caps**: High-frequency intent submissions ($> 5\text{ req/s}$) trigger instant agent suspension.
* **Geographic Anomaly Detection**: Requests originating from IPs outside the account owner's registered country incur severe risk penalties.
* **MCC Category Restrictions**: Payments targeting high-risk merchant categories (gambling, unregulated crypto) are blocked by default.
