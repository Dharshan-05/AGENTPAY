# AGENTPAY — 19: `@agentpay/events` Transactional Outbox Package Specs

## 1. Outbox Event Infrastructure

* `@agentpay/events` defines typed domain event payloads (`PaymentCreated`, `PaymentAuthorized`, `RefundRequested`).
* Exposes `outboxPublisher.publish(event, dbTx)` to atomically insert events into `outbox_events` inside database transactions.
