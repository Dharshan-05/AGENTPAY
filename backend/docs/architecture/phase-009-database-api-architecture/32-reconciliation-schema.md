# AGENTPAY — 32: `reconciliation_records` & `reconciliation_items` Schemas

## 1. `reconciliation_records` Table DDL

```sql
CREATE TABLE reconciliation_records (
    reconciliation_id VARCHAR(64) PRIMARY KEY,
    provider VARCHAR(32) NOT NULL DEFAULT 'razorpay',
    batch_reference VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED',
    total_matched INT NOT NULL DEFAULT 0,
    total_discrepancies INT NOT NULL DEFAULT 0,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
