# AGENTPAY — 82: Redis API Read Caching & Invalidation Strategy

## 1. API Caching Rules

* **Read Caching**: Read-heavy non-financial endpoints (`GET /api/v1/products`, `GET /api/v1/merchants`) use Redis read-aside caching with 5-minute TTLs.
* **Immediate Invalidation**: Mutations (`POST /api/v1/products`) immediately invalidate associated Redis cache keys (`DEL cache:products:*`).
