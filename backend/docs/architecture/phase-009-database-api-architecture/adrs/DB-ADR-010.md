# DB-ADR-010: Database Trigger Enforcement for Double-Entry Equilibrium

## Context & Problem Statement
Preventing unbalanced financial ledger entries requires database-enforced integrity checks.

## Decision
Create a PostgreSQL trigger function (`verify_ledger_transaction_balance`) enforcing $\sum \text{Debit} = \sum \text{Credit}$.

## Consequences & Trade-Offs
* **Benefits**: Rejects unbalanced transactions at the database engine level.
* **Trade-Offs**: Adds slight execution overhead to ledger inserts.
