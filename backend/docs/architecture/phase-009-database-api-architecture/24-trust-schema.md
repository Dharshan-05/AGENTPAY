# AGENTPAY — 24: `trust_assessments` & `trust_scores` Historical Schemas

## 1. `trust_scores` Table DDL

```sql
CREATE TABLE trust_scores (
    trust_score_id VARCHAR(64) PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL REFERENCES agents(agent_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    score INT NOT NULL CHECK (score BETWEEN 0 AND 100),
    factors JSONB NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_trust_agent ON trust_scores(agent_id, calculated_at DESC);
```
