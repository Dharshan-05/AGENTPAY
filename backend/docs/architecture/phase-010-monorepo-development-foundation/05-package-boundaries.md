# AGENTPAY — 05: Shared Package Boundaries & Ownership Taxonomy

## 1. Package Responsibility Matrix

* `@agentpay/config`: Strictly contains environment schema validation (`Zod`). Zero business logic.
* `@agentpay/types`: Pure TypeScript type interfaces and enums. Zero runtime dependencies.
* `@agentpay/api-contracts`: Shared Zod validation schemas for requests, responses, and errors.
* `@agentpay/database`: Encapsulates PostgreSQL connection pools, Kysely/Prisma schema, migrations, and base repositories.
* `@agentpay/payments`: Encapsulates Razorpay API client, state machine transitions, and double-entry ledger helpers.
* `@agentpay/agentguard-core`: Encapsulates 6-stage policy verification rules and risk evaluation interfaces.
