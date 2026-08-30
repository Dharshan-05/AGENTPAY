# AGENTPAY — 04: Authoritative Source of Truth, Derived Data & Cache Map

## 1. Domain Data Authority Mapping

```
+-----------------------------------------------------------------------+
|                       AUTHORITATIVE DATA SOURCE MAP                   |
+-----------------------------------------------------------------------+
|  Domain Entity     | Authoritative Store | Derived Store | Cache Store|
+--------------------+---------------------+---------------+------------+
|  Payment Status    | PostgreSQL Database | Analytics DB  | Redis TTL  |
|  Ledger Balances   | PostgreSQL Ledger   | Dashboard     | Redis Cache|
|  Agent Identity    | PostgreSQL DB       | JWT Tokens    | Redis Auth |
|  Policy Rules      | PostgreSQL DB       | In-Memory Engine| Redis    |
|  Risk Model Score  | Python FASTAPI      | PostgreSQL DB | Redis TTL  |
|  Idempotency Key   | Redis 24h SETNX     | PostgreSQL DB | Redis      |
|  Webhook Event ID  | PostgreSQL DB       | Analytics DB  | Redis      |
+-----------------------------------------------------------------------+
```

PostgreSQL is the single, non-negotiable authoritative source of truth for all financial transactions, ledger balances, and audit records. Redis and analytics stores contain strictly ephemeral or derived data.
