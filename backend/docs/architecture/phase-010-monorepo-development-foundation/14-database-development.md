# AGENTPAY — 14: `@agentpay/database` Client & Repository Package Specs

## 1. Database Package Responsibilities

* `@agentpay/database` centralizes PostgreSQL pool creation, TypeORM/Prisma schema definitions, and base repository patterns.
* Exposes utility functions: `db.transaction()`, `db.setTenantContext(tenantId)`, `db.verifyHealth()`.
* **No Business Logic**: Domain logic resides strictly in application services.
