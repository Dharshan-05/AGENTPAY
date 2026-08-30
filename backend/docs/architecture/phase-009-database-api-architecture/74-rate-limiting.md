# AGENTPAY — 74: Redis Sliding-Window Multi-Tier Rate Limiting Engine

## 1. Rate Limiting Multi-Tier Matrix

| API Tier | Limit | Window | Key Structure |
| :--- | :--- | :--- | :--- |
| **Agent Payment Intents** | 100 req | 60 sec | `rl:agent:<agent_id>:intents` |
| **User REST APIs** | 300 req | 60 sec | `rl:user:<user_id>:api` |
| **Public Webhook Ingress** | 1000 req | 60 sec | `rl:ip:<ip_address>:webhooks` |

Requests exceeding limits receive HTTP 429 Too Many Requests with `Retry-After` headers.
