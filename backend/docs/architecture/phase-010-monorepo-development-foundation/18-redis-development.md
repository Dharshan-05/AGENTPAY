# AGENTPAY — 18: Local Redis Development Container & Caching Setup

## 1. Local Redis Service Config

* **Image**: `redis:7-alpine`
* **Container Name**: `agentpay-redis`
* **Port**: `6379`
* **Use Cases**: Idempotency locks (24h TTL), API rate limit counters, Pub/Sub event distribution.
