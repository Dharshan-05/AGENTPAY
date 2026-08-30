# AGENTPAY — 88: End-to-End Payment Intent Flow Traceability Chain

## 1. Traceability Chain

```
POST /payment-intents
 ↓
PaymentIntent (status = CREATED)
 ↓
RiskDecision (risk_score = 16)
 ↓
PolicyVersion (active_v1)
 ↓
PaymentAuthorization (token_signed)
 ↓
Payment (status = PROCESSING)
 ↓
PaymentAttempt (attempt_1)
 ↓
ProviderPaymentID (pay_K123456789)
 ↓
WebhookEvent (payment.captured)
 ↓
PaymentEvent (PaymentSucceeded)
 ↓
LedgerTransaction (posted)
 ↓
ReconciliationRecord (MATCHED)
 ↓
AuditEvent (block_hash_signed)
```
