# AGENTPAY — 21: Append-Only Cryptographic Block Hash Audit Chains

## 1. SHA-256 Block Hashing Chain

$$\text{BlockHeader}_n = \text{Hash}_{n-1} \parallel \text{Timestamp}_n \parallel \text{EventType}_n \parallel \text{Actor}_n \parallel \text{TargetID}_n \parallel \text{PayloadHash}_n$$

$$\text{Hash}_n = \text{SHA256}(\text{BlockHeader}_n)$$

---

## 2. Immutable Storage Controls

Audit log database table (`audit_logs`) permissions strictly deny `UPDATE` and `DELETE` queries. Any attempt to modify a past entry breaks the cryptographic hash chain, triggering instant security alarms.
