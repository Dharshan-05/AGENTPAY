# AGENTPAY — 26: `approval_requests` Table Schema & 15m Expiration TTL

## 1. `approval_requests` Table DDL

```sql
CREATE TABLE approval_requests (
    approval_id VARCHAR(64) PRIMARY KEY,
    payment_intent_id VARCHAR(64) NOT NULL REFERENCES payment_intents(payment_intent_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    requester_agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    approver_user_id VARCHAR(64),
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'EXPIRED'
    reason TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMPTZ
);

CREATE INDEX idx_approval_status ON approval_requests(tenant_id, status);
```
