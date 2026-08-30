# AGENTPAY — 23: Multi-Tier Redis Rate Limiting Architecture

## 1. Rate Limiting Limits

* **Per Agent**: Max 60 requests/minute.
* **Per User Account**: Max 300 requests/minute.
* **Per Ingress IP**: Max 120 requests/minute.
* **Per Gateway Webhook Endpoint**: Max 500 requests/minute.

Exceeding limits returns HTTP 429 `Too Many Requests` with `Retry-After` header.
