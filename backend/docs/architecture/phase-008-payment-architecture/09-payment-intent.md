# AGENTPAY — 09: `PaymentIntent` Schema, Lifecycle & State Rules

## 1. `PaymentIntent` Schema

```json
{
  "payment_intent_id": "intent_7f8a9b0c-1d2e-3f4a",
  "tenant_id": "tenant_7f8a9b0c",
  "user_id": "usr_91a0b2c3",
  "agent_id": "agt_8f9b2c3a",
  "order_id": "ord_3f2a1b0c",
  "merchant_id": "mch_12345678",
  "amount": 250000,
  "currency": "INR",
  "status": "CREATED",
  "idempotency_key": "idemp_uuid_v4",
  "expires_at": "2026-08-24T22:35:00Z",
  "created_at": "2026-08-24T22:20:00Z"
}
```

---

## 2. Intent Preconditions

`PaymentIntent` represents a proposed transaction payload before policy authorization. Amounts are specified in minor units (`250000` = ₹2,500.00). Unsubmitted intents expire after 15 minutes.
