# AGENTPAY — 46: Transactional Outbox Pattern for Atomic Event Dispatch

## 1. Outbox Pattern Architecture

To prevent dual-write discrepancies (DB updated but Redis Pub/Sub notification fails):

```sql
BEGIN;

-- 1. Update Payment Record
UPDATE payment_intents SET status = 'EXECUTED' WHERE payment_intent_id = 'intent_123';

-- 2. Insert Event into Transactional Outbox Table
INSERT INTO outbox_events (event_id, event_type, payload) VALUES ('evt_456', 'PaymentSucceeded', '{...}');

COMMIT;
```

A background worker polls `outbox_events` and publishes events to Redis Pub/Sub, guaranteeing atomic event delivery.
