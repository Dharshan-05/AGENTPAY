# AGENTPAY — 16: 18-State Payment Machine Persistence & Optimistic Locking

## 1. Concurrency Versioning SQL Execution

Every state transition enforces optimistic locking via the `version` column:

```sql
UPDATE payment_intents
SET status = 'AUTHORIZED',
    version = version + 1,
    updated_at = NOW()
WHERE payment_intent_id = 'intent_7f8a9b0c'
  AND status = 'RISK_CHECK'
  AND version = 1;
```

If zero rows are updated, the application detects a concurrent update conflict and aborts execution.
