# API-ADR-004: Multi-Tier Authorization (RBAC + ABAC + Scopes)

## Context & Problem Statement
Basic role-based checks cannot evaluate dynamic agent spending caps or category policy rules.

## Decision
Enforce a 3-layer authorization pipeline combining RBAC roles, ABAC contextual rules, and Agent Capability Scopes.

## Consequences & Trade-Offs
* **Benefits**: Fine-grained access control preventing privilege escalation.
* **Trade-Offs**: Requires evaluating policy scopes on every request.
