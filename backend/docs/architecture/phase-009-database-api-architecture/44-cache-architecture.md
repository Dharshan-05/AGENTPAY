# AGENTPAY — 44: Redis Derived Data Caching, TTL & Cache Invalidation Rules

## 1. Caching Policy Rules

* **Authoritative Data Exclusion**: Ephemeral Redis stores session states, idempotency locks (24h TTL), sliding-window rate limits, and non-authoritative read-aside product catalog queries.
* **Financial Data Ban**: Primary payment status records, ledger balances, and audit logs are NEVER read exclusively from Redis cache when processing financial transactions.
