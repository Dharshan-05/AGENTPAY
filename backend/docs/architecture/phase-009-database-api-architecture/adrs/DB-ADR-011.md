# DB-ADR-011: Transaction Isolation Level Assignment (`READ COMMITTED` vs `SERIALIZABLE`)

## Context & Problem Statement
Balancing database query performance with financial settlement serializability.

## Decision
Use `READ COMMITTED` for general read queries; use `SERIALIZABLE` or `READ COMMITTED` with `FOR UPDATE` locks for payment state transitions.

## Consequences & Trade-Offs
* **Benefits**: Optimizes read throughput while guaranteeing settlement isolation.
* **Trade-Offs**: Applications must handle serialization retry errors (`40001`).
