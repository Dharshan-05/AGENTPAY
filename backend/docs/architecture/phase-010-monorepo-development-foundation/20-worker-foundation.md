# AGENTPAY — 20: `apps/worker` Background Execution Architecture

## 1. Background Worker Tasks

* **Outbox Poller**: Queries `outbox_events WHERE status = 'PENDING'` every 1,000ms.
* **Webhook Processor**: Consumes Razorpay webhook events from Redis queue asynchronously.
* **Reconciliation Job**: Executes daily settlement audit tasks.
