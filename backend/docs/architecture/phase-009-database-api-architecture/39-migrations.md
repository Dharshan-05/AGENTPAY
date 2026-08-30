# AGENTPAY — 39: Database Migration Governance, Versioning & Rollback Rules

## 1. Migration Standards

* **Tooling**: Node.js Prisma / TypeORM or Golang `golang-migrate` executed via automated CI/CD pipelines.
* **Naming**: Prefix timestamps (`20260824230000_create_payments.sql`).
* **Forward-Only Rule**: Production migrations deploy backward-compatible SQL steps (Expand/Contract pattern) rather than destructive rollbacks.
