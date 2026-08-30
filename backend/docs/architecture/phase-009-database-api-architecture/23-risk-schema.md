# AGENTPAY — 23: `risk_assessments` & `risk_decisions` Immutable Schemas

## 1. Risk Data Schemas

```sql
CREATE TABLE risk_assessments (
    risk_assessment_id VARCHAR(64) PRIMARY KEY,
    payment_intent_id VARCHAR(64) NOT NULL REFERENCES payment_intents(payment_intent_id),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(tenant_id),
    risk_score INT NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    risk_level VARCHAR(32) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH'
    decision VARCHAR(32) NOT NULL, -- 'ALLOW', 'REVIEW', 'BLOCK'
    model_version VARCHAR(32) NOT NULL,
    features JSONB NOT NULL,
    xai_explanation JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_intent ON risk_assessments(payment_intent_id);
```
