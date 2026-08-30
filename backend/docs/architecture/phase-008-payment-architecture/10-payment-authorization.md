# AGENTPAY — 10: Cryptographic `PaymentAuthorizationContext` Specs

## 1. Authorization Context Payload

Issued exclusively by AGENTGUARD upon passing policy rules and risk evaluation:

```json
{
  "authorization_id": "auth_9f8a7b6c-5d4e",
  "payment_intent_id": "intent_7f8a9b0c",
  "agent_id": "agt_8f9b2c3a",
  "tenant_id": "tenant_7f8a9b0c",
  "amount": 250000,
  "currency": "INR",
  "merchant_id": "mch_12345678",
  "risk_score": 14,
  "trust_score": 88,
  "policy_version": "v1.4.0",
  "expires_at": "2026-08-24T22:35:00Z",
  "signature": "hmac_sha256_authorization_signature"
}
```

---

## 2. Inviolable Authorization Rules

* **Short-Lived**: Expires 15 minutes after issuance.
* **Non-Transferable**: Cryptographically bound to `intent_id`, `agent_id`, `amount`, and `merchant_id`.
* **Single-Use**: Evicted from Redis upon Payment Orchestrator dispatch; cannot be reused for duplicate settlements.
