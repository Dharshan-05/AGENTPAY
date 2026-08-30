# AGENTPAY — 10: Data Flow & Cryptographic Audit Block Hash Pipeline

## 1. Data Flow Architecture

This document details the data pipeline from intent submission to append-only cryptographic block hashing.

```mermaid
graph TD
    AGENT[AI Agent Request] --> GW[API Gateway Validation]
    GW --> LOCK{Acquire Redis Idempotency Lock}
    LOCK -- Acquired --> GUARD[AGENTGUARD Policy Check]
    GUARD --> FRAUD[FRAUDGUARD Feature & ML Scoring]
    FRAUD --> XAI[XAI Explanation Synthesis]
    XAI --> DECISION{Decision Gate}
    DECISION -- ALLOW --> EXEC[Payment Settlement Execution]
    DECISION -- REVIEW --> QUEUE[Approval Queue & Notification]
    DECISION -- BLOCK --> LOG_BLOCK[Write Block Audit Entry]
    QUEUE --> HUMAN[Human Approval Action]
    HUMAN -- Approved --> EXEC
    HUMAN -- Rejected --> LOG_REJECT[Write Rejection Audit Entry]
    EXEC --> DB_WRITE[Write Relational Intent Record]
    DB_WRITE --> AUDIT_HASH[Compute SHA-256 Block Hash: H_n = SHA256(H_n-1 || Payload)]
    AUDIT_HASH --> AUDIT_DB[(Append-Only Audit Log Table)]
```

---

## 2. Cryptographic Block Hash Algorithm

$$\text{BlockHeader}_n = \text{Hash}_{n-1} \parallel \text{Timestamp}_n \parallel \text{EventType}_n \parallel \text{Actor}_n \parallel \text{TargetID}_n \parallel \text{PayloadHash}_n$$

$$\text{Hash}_n = \text{SHA256}(\text{BlockHeader}_n)$$

This guarantees tamper evidence: altering any historical audit log entry invalidates all subsequent block hashes in the database.
