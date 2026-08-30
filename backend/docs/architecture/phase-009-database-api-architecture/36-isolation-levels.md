# AGENTPAY — 36: Transaction Isolation Levels (`READ COMMITTED` vs `SERIALIZABLE`)

## 1. Isolation Level Assignment

* **Default Isolation Level**: `READ COMMITTED` for high-throughput query read operations.
* **Financial Settlement Level**: `SERIALIZABLE` or `READ COMMITTED` with `FOR UPDATE` row locks for payment state machine updates, ledger journal entries, and budget counter increments.
