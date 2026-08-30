# AGENTPAY — 13: `orders` Relational Table Schema & Constraint Definitions

## 1. `orders` Table SQL DDL

```sql
CREATE TABLE orders (
    order_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id),
    agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    merchant_id VARCHAR(64) NOT NULL REFERENCES merchants(merchant_id),
    status VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    subtotal NUMERIC(18,4) NOT NULL CHECK (subtotal >= 0),
    tax NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (tax >= 0),
    discount NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (discount >= 0),
    total NUMERIC(18,4) NOT NULL CHECK (total >= 0),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_orders_total_math CHECK (total = (subtotal + tax - discount))
);

CREATE INDEX idx_orders_tenant_user ON orders(tenant_id, user_id);
CREATE INDEX idx_orders_tenant_agent ON orders(tenant_id, agent_id);
```
