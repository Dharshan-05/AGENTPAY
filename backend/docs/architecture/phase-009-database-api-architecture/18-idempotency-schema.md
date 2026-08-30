# AGENTPAY — 18: `idempotency_records` Table Schema & 24h Expiration Rules

## 1. `idempotency_records` DDL

```sql
CREATE TABLE idempotency_records (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    idempotency_key VARCHAR(128) NOT NULL,
    operation VARCHAR(64) NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64),
    response_code INT NOT NULL,
    response_body JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_idempotency_tenant_op_key UNIQUE(tenant_id, operation, idempotency_key)
);

CREATE INDEX idx_idempotency_expires ON idempotency_records(expires_at);
```
