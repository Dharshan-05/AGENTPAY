# AGENTPAY — 56: AGENTGUARD Security Control Plane API Contracts

## 1. AGENTGUARD Evaluation Endpoint

* `POST /api/v1/agentguard/evaluate`: Internal REST interface evaluating proposed payment intent against 6-stage security policy rules and FRAUDGUARD ML risk scores.

### Input Request Payload

```json
{
  "payment_intent_id": "intent_7f8a9b0c",
  "agent_id": "agt_8f9b2c3a",
  "amount": 250000,
  "currency": "INR",
  "merchant_id": "mch_12345678"
}
```

### Output Response Payload

```json
{
  "decision_id": "dec_9f8a7b6c",
  "decision": "ALLOW",
  "risk_score": 16,
  "trust_score": 88,
  "authorization_token": "auth_9f8a7b6c-signed-token"
}
```
