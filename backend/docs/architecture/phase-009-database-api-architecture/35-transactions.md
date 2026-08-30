# AGENTPAY — 35: Atomic Database Transaction Boundaries & ACID Rules

## 1. Atomic Financial Boundaries

Financial state changes execute within single, atomic PostgreSQL transaction blocks (`BEGIN` ... `COMMIT`):

1. **State Update**: Transition payment state from `AUTHORIZED` to `PROCESSING`.
2. **Outbox Insertion**: Insert domain event into `outbox_events`.
3. **Audit Log Insertion**: Insert audit log block into `audit_events`.
