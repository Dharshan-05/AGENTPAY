# AGENTPAY — 87: Complete API Endpoint to DB Schema Traceability Matrix

## 1. Traceability Mapping

| API Endpoint | Application Controller | Primary Repository | PostgreSQL Target Table | Transaction Type |
| :--- | :--- | :--- | :--- | :--- |
| `POST /payment-intents` | `PaymentIntentController` | `PaymentIntentRepository`| `payment_intents` | READ COMMITTED |
| `POST /agentguard/evaluate`| `AgentGuardController` | `PolicyRepository` | `payment_authorizations` | SERIALIZABLE |
| `POST /payments/execute` | `PaymentController` | `PaymentRepository` | `payments`, `outbox_events` | SERIALIZABLE |
| `POST /webhooks/razorpay` | `WebhookController` | `WebhookRepository` | `webhook_events`, `payments` | READ COMMITTED |
| `POST /refunds` | `RefundController` | `RefundRepository` | `refunds`, `ledger_entries` | SERIALIZABLE |
