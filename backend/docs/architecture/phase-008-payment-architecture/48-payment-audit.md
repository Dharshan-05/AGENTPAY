# AGENTPAY — 48: SHA-256 Append-Only Audit Logging Chain

## 1. Audit Chain Algorithm

$$\text{BlockHeader}_n = \text{Hash}_{n-1} \parallel \text{Timestamp}_n \parallel \text{PaymentID}_n \parallel \text{Actor}_n \parallel \text{StateChange}_n \parallel \text{PayloadHash}_n$$

$$\text{Hash}_n = \text{SHA256}(\text{BlockHeader}_n)$$

Database permissions deny `UPDATE` and `DELETE` queries on `audit_logs`, providing immutable mathematical proof of transaction histories.
