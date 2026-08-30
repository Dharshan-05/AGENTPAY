# AGENTPAY — 11: Payment Authorization Context & Replay Defenses

## 1. Payment Authorization Token Context

Payment execution requires a cryptographically signed `Payment Authorization Context` issued by AGENTGUARD:

```json
{
  "authorization_id": "auth_9f8a7b6c",
  "intent_id": "intent_7f8a9b0c",
  "agent_id": "agt_8f9b2c3a",
  "tenant_id": "tenant_7f8a9b",
  "amount": 250000,
  "currency": "INR",
  "merchant_domain": "trusted-electronics.in",
  "risk_score": 12,
  "expires_at": "2026-08-24T21:30:00Z",
  "signature": "hmac_sha256_auth_signature"
}
```

---

## 2. Replay & Double-Spend Defense

* **Idempotency Key Lock**: Redis 24-hour distributed lock on `idempotency_key`.
* **Short-Lived Authorization**: Payment authorization tokens expire in 15 minutes.
* **State Machine Guard**: Intent must exist in `AUTHORIZED` state; state jumps strictly blocked.
