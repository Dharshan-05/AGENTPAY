# PAY-ADR-006: 18-State Transaction Lifecycle State Machine

## Context & Problem Statement
Payment processing involves multiple asynchronous stages (risk evaluation, provider dispatch, webhooks) that risk invalid state transitions if unconstrained.

## Decision
Enforce a formal 18-state payment transaction state machine with strict transition authority rules.

## Consequences & Trade-Offs
* **Benefits**: Eliminates race conditions and illegal status updates.
* **Trade-Offs**: State updates must execute inside database transactions.
