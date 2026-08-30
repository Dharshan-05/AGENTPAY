# AGENTPAY — 36: 8 Invariant Financial Integrity Rules

## 1. Invariant Rules

1. Zero negative refundable balances.
2. Zero duplicate payments cleared for identical idempotency keys.
3. Zero unauthorized refunds.
4. Zero cross-tenant data access or payment routing.
5. Zero amount mutation post-authorization context issuance.
6. Zero currency code mutation post-authorization.
7. Zero illegal state machine transitions.
8. Zero double-entry accounting ledger imbalances ($\sum \text{Debit} = \sum \text{Credit}$).
