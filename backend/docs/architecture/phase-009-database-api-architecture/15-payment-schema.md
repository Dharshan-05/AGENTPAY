# AGENTPAY — 15: `payment_intents`, `payments`, `payment_attempts` Schemas

## 1. Core Payment DDL

```sql
CREATE TABLE payment_intents (
    payment_intent_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id),
    agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    order_id VARCHAR(64) NOT NULL REFERENCES orders(order_id),
    merchant_id VARCHAR(64) NOT NULL REFERENCES merchants(merchant_id),
    amount NUMERIC(18,4) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    idempotency_key VARCHAR(128) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_payment_intent_idempotency UNIQUE(tenant_id, idempotency_key)
);

CREATE TABLE payments (
    payment_id VARCHAR(64) PRIMARY KEY,
    payment_intent_id VARCHAR(64) NOT NULL REFERENCES payment_intents(payment_intent_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    amount NUMERIC(18,4) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL DEFAULT 'PROCESSING',
    provider_payment_id VARCHAR(128) UNIQUE,
    provider_order_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
