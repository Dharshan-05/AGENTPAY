# AGENTPAY — 29: `audit_events` Append-Only SHA-256 Block Chain Table Schema

## 1. `audit_events` Table DDL

```sql
CREATE TABLE audit_events (
    audit_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    actor_id VARCHAR(64) NOT NULL,
    actor_type VARCHAR(32) NOT NULL, -- 'USER', 'AGENT', 'SYSTEM'
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(64) NOT NULL,
    prev_hash VARCHAR(64) NOT NULL,
    block_hash VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    trace_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Deny UPDATE and DELETE on audit_events
REVOKE UPDATE, DELETE ON audit_events FROM PUBLIC, agentpay_app;
```
