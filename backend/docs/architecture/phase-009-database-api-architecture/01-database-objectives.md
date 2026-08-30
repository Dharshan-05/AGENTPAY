# AGENTPAY — 01: Database Core Objectives & Non-Negotiable Financial Invariants

## 1. Core Database Objectives

The primary objective of the AGENTPAY Database Architecture is to establish an ACID-compliant, highly reliable, fail-closed relational PostgreSQL persistence engine for autonomous AI transactions and financial ledger management.

---

## 2. 15 Non-Negotiable Critical Financial Invariants

1. **Zero Cross-Tenant Access**: Row-Level Security (RLS) policies enforce strict multi-tenant isolation on 100% of tenant-scoped tables (`WHERE tenant_id = app.current_tenant`).
2. **Zero Duplicate Financial Execution**: Database unique key constraints (`UNIQUE(tenant_id, idempotency_key)`) mathematically prevent double-charge events.
3. **Zero Over-Refund**: Cumulative refund balances enforce hard relational constraints ($\sum \text{Refunds} \le \text{PaymentAmount}$).
4. **Zero Unauthorized Payment State Mutation**: Payment state transitions are strictly governed by state machine validation inside PostgreSQL transactions.
5. **Zero Floating-Point Financial Amounts**: Monetary values are stored exclusively using PostgreSQL `NUMERIC(18,4)` or integer minor units.
6. **Zero Client-Controlled Tenant Context**: `tenant_id` context is set server-side via trusted session configuration (`app.current_tenant`).
7. **Immutable Financial History**: Historical payment records, ledger entries, and audit logs are append-only. `UPDATE` and `DELETE` queries are strictly prohibited on ledger and audit tables.
8. **Double-Entry Accounting Ledger Equilibrium**: Every financial journal transaction enforces balanced debit and credit entries ($\sum \text{Debits} = \sum \text{Credits}$).
9. **Transactional Outbox Event Consistency**: Domain state updates and domain event creation execute inside identical database transactions.
10. **Zero Plaintext Secrets**: Zero gateway secret keys, API keys, or raw passwords stored in plaintext inside database tables.
11. **Isolated Provider Identifiers**: Internal primary keys are strictly decoupled from external provider IDs (e.g. `payment_id` vs `provider_payment_id`).
12. **Authoritative State Persistence**: Relational database records are the sole source of truth for payment status, overriding LLM text or frontend state claims.
13. **Strict Foreign Key Constraints**: All relational references enforce `ON DELETE RESTRICT` to prevent accidental cascading data purges.
14. **Pessimistic Concurrency Locking**: Critical state updates execute using `SELECT FOR UPDATE` to eliminate race conditions.
15. **Fail-Closed Security Default**: Outages, database locks, or constraint violations fail closed, aborting transaction execution.
