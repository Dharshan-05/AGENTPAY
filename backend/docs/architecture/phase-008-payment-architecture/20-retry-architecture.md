# AGENTPAY — 20: State-Aware Exponential Backoff & Jitter Retry Engine

## 1. Retry Eligibility Matrix

* **`RETRYABLE`**: Network socket timeouts, HTTP 503 Provider Temporarily Unavailable. *Policy*: Exponential backoff with full jitter ($1\text{s}, 2\text{s}, 4\text{s}$), max 3 attempts.
* **`NON_RETRYABLE`**: Invalid card CVV, insufficient funds, policy breach, invalid single limit. *Policy*: Fail fast immediately; retry strictly forbidden.
* **`UNKNOWN`**: Provider timeout ($> 5,000\text{ ms}$). *Policy*: Retry strictly forbidden until state is verified via GET API or reconciliation.
