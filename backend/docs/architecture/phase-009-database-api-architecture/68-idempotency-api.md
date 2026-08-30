# AGENTPAY — 68: Ingress API Endpoint Idempotency Header Execution Rules

## 1. Idempotency Header Architecture

Clients submit UUID v4 keys via `Idempotency-Key` headers on state-mutating requests:

```
POST /api/v1/payments/execute
Idempotency-Key: 7f8a9b0c-1d2e-3f4a-5b6c-7d8e9f0a1b2c
```

1. **New Key**: Process transaction, lock Redis key for 24 hours, cache response.
2. **Replayed Key**: Return cached HTTP response immediately.
3. **Mismatched Request Body**: Return HTTP 409 Conflict (`ERR_IDEMPOTENCY_KEY_REUSE`).
