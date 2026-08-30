# DB-ADR-009: Double-Entry Financial Accounting Ledger Storage

## Context & Problem Statement
Mutable user balances risk financial corruption and lack historical audit trail clarity.

## Decision
Implement double-entry accounting ledger tables (`ledger_accounts`, `ledger_transactions`, `ledger_entries`).

## Consequences & Trade-Offs
* **Benefits**: Complete auditability; mathematical guarantee that debits equal credits.
* **Trade-Offs**: Account balances must be calculated from historical entries.
