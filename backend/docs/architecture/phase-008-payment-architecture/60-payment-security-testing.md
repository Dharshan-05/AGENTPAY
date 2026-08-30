# AGENTPAY — 60: Automated Payment Security & Double-Spend Test Suite

## 1. Security Test Suite

* **Double-Spend Test**: Executes 100 parallel requests with identical idempotency key; verifies exactly 1 settlement clears.
* **Over-Refund Test**: Attempts to execute refunds exceeding original amount; verifies 100% rejection rate.
* **Webhook Forgery Test**: Submits fake webhooks with invalid HMAC signatures; verifies 100% rejection with HTTP 401.
