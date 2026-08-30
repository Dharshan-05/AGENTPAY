# PAY-ADR-014: Immutable Append-Only Financial Ledger

## 1. Context & Problem Statement
Modifying historical payment database records destroys financial auditability.

## 2. Decision
Maintain an append-only, immutable financial ledger. Record corrections exclusively using compensating reversal journal entries.

## 3. Consequences & Trade-Offs
* **Benefits**: Guarantees complete historical financial auditability.
* **Trade-Offs**: Requires double-entry bookkeeping logic.
