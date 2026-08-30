# PAY-ADR-004: Payment Intent Entity Decoupling

## Context & Problem Statement
AI agents proposing purchases should not directly trigger financial settlements before security policy evaluation.

## Decision
Introduce a `PaymentIntent` entity that represents an uncommitted financial proposal subject to AGENTGUARD policy checks.

## Consequences & Trade-Offs
* **Benefits**: Creates a clear phase boundary between intent proposal and execution.
* **Trade-Offs**: Requires managing intent expiration state transitions.
