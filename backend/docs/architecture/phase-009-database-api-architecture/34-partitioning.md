# AGENTPAY — 34: PostgreSQL Time-Based Declarative Table Partitioning Specs

## 1. Time-Based Partitioning Strategy

High-volume tables (`audit_events`, `outbox_events`, `webhook_events`) use PostgreSQL 14+ Range Partitioning by month on `created_at`:

```sql
CREATE TABLE audit_events (
    audit_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_events_y2026m08 PARTITION OF audit_events
    FOR VALUES FROM ('2026-08-01 00:00:00+00') TO ('2026-09-01 00:00:00+00');
```
