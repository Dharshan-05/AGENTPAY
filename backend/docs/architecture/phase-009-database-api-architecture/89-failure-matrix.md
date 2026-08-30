# AGENTPAY — 89: Master API & Database System Failure Recovery Matrix

## 1. System Failure Recovery Matrix

| Failure Mode | Detection Mechanism | System State Impact | Recovery Action | User Communication |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL Connection Outage** | Health Check Timeout | Ingress API Fail-Closed | Patroni Failover to Standby Database | HTTP 503 Service Temporarily Unavailable |
| **Redis Cache Outage** | Redis Socket Exception | API falls back to Direct DB | Bypasses cache read; uses DB queries | Normal API Execution (Increased Latency) |
| **Razorpay API Timeout (5s)** | Gateway HTTP Timeout | State: `PAYMENT_STATUS_UNKNOWN`| Async Verification Job Queries Status | Payment Under Verification Notification |
| **Webhook Processing Failure** | Worker Error Log | Queue Retry Backoff | Outbox Poller / Webhook Worker Retries | Delayed Payment Update Notification |
