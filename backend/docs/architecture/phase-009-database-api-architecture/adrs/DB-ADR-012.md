# DB-ADR-012: Pessimistic DB Row Locking (`SELECT FOR UPDATE`) Protocol

## Context & Problem Statement
Preventing parallel execution workers from processing identical payment intents simultaneously.

## Decision
Enforce `SELECT FOR UPDATE` pessimistic row locking inside atomic transactions during payment processing.

## Consequences & Trade-Offs
* **Benefits**: Guarantees exclusive row access during gateway settlement dispatch.
* **Trade-Offs**: Requires keeping database transaction hold times under 50ms.
