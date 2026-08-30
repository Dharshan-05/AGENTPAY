# SEC-ADR-003: Hybrid RBAC + ABAC Scoped Capability Authorization

## Context & Problem Statement
Simple role-based checks cannot evaluate dynamic attributes like daily spending caps, MCC restrictions, or risk score thresholds.

## Threat Analysis
An agent with broad execution roles could make unauthorized purchases exceeding user intentions.

## Decision
Implement a hybrid RBAC + ABAC model where RBAC establishes coarse principal roles, while ABAC and scoped tokens (`spend:intent_create`) enforce dynamic contextual constraints.

## Consequences & Trade-Offs
* **Benefits**: Fine-grained capability control over AI agent actions.
* **Trade-Offs**: Requires evaluating multi-attribute rules on every intent request.
