# SEC-ADR-005: Agent Capability Scopes & Least Privilege

## Context & Problem Statement
Agents created for product discovery should not possess authorization to execute payments unless explicitly granted.

## Threat Analysis
Over-privileged agents could be manipulated via prompt injection to execute unintended fund transfers.

## Decision
Mandate explicit capability scope tokens (`spend:intent_create`, `cart:create`, `product:search`). Unscoped actions fail closed.

## Consequences & Trade-Offs
* **Benefits**: Strictly limits blast radius of compromised agents.
* **Trade-Offs**: Requires human owners to configure scope permissions upon enrollment.
