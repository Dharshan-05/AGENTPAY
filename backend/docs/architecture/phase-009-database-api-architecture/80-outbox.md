# AGENTPAY — 80: Transactional Outbox Pattern API Dispatch Integration

## 1. Outbox Worker Integration

```
[ API Controller ] ──(DB Transaction)──> 1. UPDATE DB State
                                         2. INSERT outbox_events
                                                     │
[ Outbox Poller Worker ] <──(Polls 'PENDING')───────┘
          │
          └──> Publish Event to Redis Pub/Sub ──> Mark 'PUBLISHED'
```
