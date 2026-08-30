# AGENTPAY — 25: `policies`, `policy_versions`, `policy_rules` Schemas

## 1. Policy Engine Relational DDL

```sql
CREATE TABLE policy_versions (
    policy_version_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    version VARCHAR(32) NOT NULL,
    rules JSONB NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tenant_policy_version UNIQUE(tenant_id, version)
);
```
