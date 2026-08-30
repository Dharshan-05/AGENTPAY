# AGENTPAY — 27: `agents`, `agent_identities`, `agent_capabilities` Schemas

## 1. `agents` Core DDL

```sql
CREATE TABLE agents (
    agent_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    name VARCHAR(128) NOT NULL,
    type VARCHAR(32) NOT NULL, -- 'COMMERCE', 'PAYMENT', 'SUPPORT'
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    autonomy_level INT NOT NULL DEFAULT 1 CHECK (autonomy_level BETWEEN 0 AND 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agent_capabilities (
    capability_id VARCHAR(64) PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    scope VARCHAR(64) NOT NULL, -- e.g., 'spend:intent_create'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_agent_capability UNIQUE(agent_id, scope)
);
```
