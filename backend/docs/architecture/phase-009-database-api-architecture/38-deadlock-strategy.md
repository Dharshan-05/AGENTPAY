# AGENTPAY — 38: Database Lock Ordering, Deadlock Detection & Retry Strategy

## 1. Deadlock Elimination Protocol

1. **Strict Lock Ordering**: Multi-table row locks must acquire locks in alphabetical table name order (`agents` $\rightarrow$ `orders` $\rightarrow$ `payment_intents`).
2. **Deadlock Timeout**: PostgreSQL `deadlock_timeout = 1s` triggers automatic rollback on deadlock detection.
3. **Application Retry**: Application catches PostgreSQL error code `40P01` (deadlock detected), retrying transaction execution up to 3 times with exponential jitter.
