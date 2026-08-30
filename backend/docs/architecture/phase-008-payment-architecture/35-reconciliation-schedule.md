# AGENTPAY — 35: Real-Time Webhook + Nightly Batch Reconciliation Jobs

## 1. Reconciliation Dual Execution Schedule

* **Real-Time Reconciliation**: Incoming webhooks trigger immediate single-transaction state reconciliation within $< 50\text{ ms}$.
* **Nightly Batch Reconciliation**: Cron job executes at `01:00 UTC` daily, fetching Razorpay settlement batch reports (`GET /v1/settlements`) and auditing 100% of transactions processed in past 24 hours.
