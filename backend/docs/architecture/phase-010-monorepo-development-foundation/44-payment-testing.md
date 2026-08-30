# AGENTPAY — 44: Payment Idempotency & Webhook Replay Test Suite

## 1. Payment Test Matrix

* **Idempotency Key Reuse**: Submits identical payment intent request twice; verifies exact cached response.
* **Webhook Replay**: Triggers duplicate Razorpay webhook POST callback; verifies single ledger posting execution.
