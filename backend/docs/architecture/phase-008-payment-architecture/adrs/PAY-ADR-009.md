# PAY-ADR-009: Pessimistic Database Row Locking (`SELECT FOR UPDATE`)

## 1. Context & Problem Statement
Concurrent execution workers handling payment state updates risk overwriting state transitions.

## 2. Decision
Use pessimistic database row locking (`SELECT FOR UPDATE`) inside atomic database transactions for payment state transitions.

## 3. Consequences & Trade-Offs
* **Benefits**: Guarantees serializable isolation during concurrent updates.
* **Trade-Offs**: Requires keeping database transactions short.
