# AGENTPAY — 81: Master API Endpoint to DB Transaction Execution Matrix

## 1. Endpoint Transaction Matrix

| Endpoint | DB Transaction | Isolation | Locking | Idempotency | Outbox Event |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST /payment-intents` | YES | READ COMMITTED | None | MANDATORY | `PaymentIntentCreated` |
| `POST /agentguard/evaluate`| YES | SERIALIZABLE | `FOR UPDATE` | MANDATORY | `PaymentAuthorized` |
| `POST /payments/execute` | YES | SERIALIZABLE | `FOR UPDATE` | MANDATORY | `PaymentInitiated` |
| `POST /webhooks/razorpay` | YES | READ COMMITTED | `FOR UPDATE` | Event Deduplication | `PaymentSucceeded` |
| `POST /refunds` | YES | SERIALIZABLE | `FOR UPDATE` | MANDATORY | `RefundRequested` |
