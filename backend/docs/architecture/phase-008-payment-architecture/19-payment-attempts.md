# AGENTPAY — 19: `PaymentAttempt` Entity Tracking & Retry Eligibility

## 1. `PaymentAttempt` Tracking Schema

Every settlement attempt dispatched to Razorpay is recorded as a discrete `PaymentAttempt` record:

```json
{
  "attempt_id": "att_5e6f7g8h",
  "payment_id": "pay_1a2b3c4d",
  "attempt_number": 1,
  "provider": "razorpay",
  "provider_order_id": "order_K987654321",
  "provider_payment_id": "pay_K123456789",
  "status": "FAILED",
  "error_code": "BAD_REQUEST_ERROR",
  "error_category": "NON_RETRYABLE",
  "started_at": "2026-08-24T22:20:01Z",
  "completed_at": "2026-08-24T22:20:03Z"
}
```
