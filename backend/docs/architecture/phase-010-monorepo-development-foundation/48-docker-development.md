# AGENTPAY — 48: Multi-Container Docker Compose (`docker-compose.yml`) Architecture

## 1. Local Infrastructure Services

* `postgres`: PostgreSQL 15-alpine on port `5432` with health check.
* `redis`: Redis 7-alpine on port `6379` with health check.
* `api`: Node.js Express API service mounted with live reload.
* `worker`: Node.js background outbox worker mounted with live reload.
