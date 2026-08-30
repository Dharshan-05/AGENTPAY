# AGENTPAY — 19: `webhook_events` Table Schema & Deduplication Constraints

## 1. `webhook_events` Table DDL

```sql
CREATE TABLE webhook_events (
    webhook_event_id VARCHAR(64) PRIMARY KEY,
    provider VARCHAR(32) NOT NULL DEFAULT 'razorpay',
    provider_event_id VARCHAR(128) NOT NULL UNIQUE,
    event_type VARCHAR(64) NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    signature_verified BOOLEAN NOT NULL DEFAULT FALSE,
    processing_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_webhook_status ON webhook_events(processing_status, received_at);
```
