# AGENTPAY — 31: `event_deliveries` Table Schema & Idempotent Consumer State

## 1. `event_deliveries` DDL

```sql
CREATE TABLE event_deliveries (
    delivery_id VARCHAR(64) PRIMARY KEY,
    outbox_event_id VARCHAR(64) NOT NULL REFERENCES outbox_events(outbox_event_id),
    consumer_name VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DELIVERED',
    delivered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_consumer_event UNIQUE(outbox_event_id, consumer_name)
);
```
