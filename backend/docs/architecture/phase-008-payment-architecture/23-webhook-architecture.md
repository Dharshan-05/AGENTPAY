# AGENTPAY — 23: Async Webhook Listener & Signature Verification Engine

## 1. Webhook Processing Flow

```
[ Razorpay Event ] ──> [ Ingress Listener ] ──> [ Verify HMAC Signature ] ──> [ Event ID Deduplication ] ──> [ Async Queue ] ──> [ State Machine Update ]
```

Incoming webhooks are verified synchronously in $< 5\text{ ms}$, acknowledged with HTTP 200 OK, and pushed to Redis Pub/Sub worker queues for asynchronous state reconciliation.
