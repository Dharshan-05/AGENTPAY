# AGENTPAY — 61: Payment Intent Proposal REST API Contract Specs

## 1. Intent Endpoints

* `POST /api/v1/payment-intents`: Create proposed transaction intent (Requires `Idempotency-Key` header).
* `GET /api/v1/payment-intents/{intent_id}`: Retrieve payment intent status.

### Request Payload Example

```json
{
  "order_id": "ord_3f2a1b0c",
  "merchant_id": "mch_12345678",
  "amount": 250000,
  "currency": "INR"
}
```
