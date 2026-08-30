# AGENTPAY — 20: `refunds` & `refund_attempts` Table Schemas & Over-Refund Guard

## 1. `refunds` Table DDL

```sql
CREATE TABLE refunds (
    refund_id VARCHAR(64) PRIMARY KEY,
    payment_id VARCHAR(64) NOT NULL REFERENCES payments(payment_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    amount NUMERIC(18,4) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    reason TEXT NOT NULL,
    requested_by VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'REQUESTED',
    provider_refund_id VARCHAR(128) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refunds_payment ON refunds(payment_id);
```
