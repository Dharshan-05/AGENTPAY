# AGENTPAY — 17: `payment_authorizations` Cryptographic Token Schema

## 1. `payment_authorizations` Table DDL

```sql
CREATE TABLE payment_authorizations (
    authorization_id VARCHAR(64) PRIMARY KEY,
    payment_intent_id VARCHAR(64) NOT NULL REFERENCES payment_intents(payment_intent_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    merchant_id VARCHAR(64) NOT NULL REFERENCES merchants(merchant_id),
    amount NUMERIC(18,4) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    risk_score INT NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    policy_version VARCHAR(32) NOT NULL,
    signature TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ISSUED',
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ
);

CREATE INDEX idx_auth_intent ON payment_authorizations(payment_intent_id);
```
