# DB-ADR-007: Relational Payment State Machine Persistence

## Context & Problem Statement
Payment transactions navigate complex asynchronous lifecycle states that must be persisted safely.

## Decision
Persist payment states in `payment_intents` and `payments` tables with optimistic concurrency (`version` column).

## Consequences & Trade-Offs
* **Benefits**: Prevents race conditions and invalid state jumps.
* **Trade-Offs**: Requires updating the `version` counter on every state transition.
