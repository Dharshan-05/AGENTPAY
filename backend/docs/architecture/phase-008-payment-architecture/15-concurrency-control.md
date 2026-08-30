# AGENTPAY — 15: Pessimistic DB Row Locking (`SELECT FOR UPDATE`)

## 1. Pessimistic Row Locking Protocol

Concurrent intent execution, daily budget updates, and refund processing execute within atomic database transactions using pessimistic row-level locks:

```sql
BEGIN;

-- Lock payment intent record for update
SELECT * FROM payment_intents 
WHERE payment_intent_id = 'intent_7f8a9b0c' 
FOR UPDATE;

-- Verify state transition precondition
UPDATE payment_intents 
SET status = 'PROCESSING' 
WHERE status = 'AUTHORIZED';

COMMIT;
```

This prevents race conditions when parallel workers process webhooks or user approval actions simultaneously.
