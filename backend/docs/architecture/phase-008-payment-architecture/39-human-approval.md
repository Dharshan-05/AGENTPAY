# AGENTPAY — 39: Escalation Approval Cards & 15-Minute Expiration TTL

## 1. Approval Card Schema

```json
{
  "approval_id": "appr_9f8a7b6c",
  "intent_id": "intent_7f8a9b0c",
  "tenant_id": "tenant_7f8a9b0c",
  "amount": 4500000,
  "currency": "INR",
  "merchant_name": "PremiumElectronics",
  "risk_score": 78,
  "xai_explanation": "Transaction requires approval. Amount (₹45,000) exceeds auto-approval limit (₹10,000).",
  "expires_at": "2026-08-24T22:35:00Z"
}
```

Approvals acquire atomic locks upon user click, issuing a single-use authorization token.
