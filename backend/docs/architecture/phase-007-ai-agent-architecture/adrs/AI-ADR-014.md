# AI-ADR-014: Human-in-the-Loop Approval Escalations

## Context & Problem Statement
High-value or ambiguous transactions require human oversight without terminating execution flows.

## Decision
Implement a 15-minute TTL escalation queue pushing interactive cards to the Approval Center UI for transactions returning `REVIEW`.

## Consequences & Trade-Offs
* **Benefits**: Balances autonomous speed with human oversight.
* **Trade-Offs**: Requires state machine management for expired intents.
