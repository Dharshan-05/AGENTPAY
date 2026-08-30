# AGENTPAY — 93: Idempotent Background Cron Job Worker Architecture

## 1. Background Worker Schedule

* **Outbox Event Publisher**: Continuous worker polling `outbox_events WHERE status = 'PENDING'` every 1,000ms.
* **Expired Authorization Cleanup**: Cron job running every 5 minutes updating `payment_authorizations SET status = 'EXPIRED' WHERE expires_at < NOW()`.
* **Nightly Reconciliation Batch**: Cron job running daily at `01:00 UTC`.
