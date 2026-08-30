# AI-ADR-010: Tool Capability Scope Pre-Execution Validation

## Context & Problem Statement
An agent assigned `product:search` should not be capable of invoking high-risk tools like `create_payment_intent`.

## Decision
Require every tool in the Tool Registry to declare a mandatory capability scope. Rejects calls if the calling `agent_id` lacks the required scope token.

## Consequences & Trade-Offs
* **Benefits**: Enforces least-privilege capability isolation at tool boundary.
* **Trade-Offs**: Requires mapping scope tokens to agent principals during enrollment.
