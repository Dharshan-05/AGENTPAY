# AGENTPAY — 15: Migration CLI Workflows (`pnpm db:migrate`)

## 1. Migration Commands

* `pnpm db:migrate`: Executes pending SQL migrations against the active database.
* `pnpm db:migrate:status`: Displays migration execution status and pending scripts.
* `pnpm db:reset`: Development-only command dropping non-production tables and re-executing migrations + seeds.
