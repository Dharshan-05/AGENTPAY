# AGENTPAY — 09: PostgreSQL Relational Database Naming Conventions (`snake_case`)

## 1. Naming Standards Matrix

* **Tables**: Plural lower `snake_case` (e.g. `payment_intents`, `ledger_entries`).
* **Columns**: Singular lower `snake_case` (e.g. `tenant_id`, `created_at`).
* **Primary Keys**: `id` or `<entity>_id` (e.g. `payment_intent_id`).
* **Foreign Keys**: `<referenced_table_singular>_id` (e.g. `user_id`, `agent_id`).
* **Indexes**: `idx_<table_name>_<column1>_<column2>` (e.g. `idx_payments_tenant_status`).
* **Unique Constraints**: `uq_<table_name>_<column>` (e.g. `uq_idempotency_tenant_key`).
