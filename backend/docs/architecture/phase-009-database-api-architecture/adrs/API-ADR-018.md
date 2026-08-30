# API-ADR-018: Privileged Administrative API RBAC Enforcement

## 1. Context & Problem Statement
Restricting access to administrative endpoints (discrepancy resolution, emergency kill switches, policy deployment).

## 2. Decision
Enforce strict `role == ADMIN` claims on `/api/v1/reconciliation/discrepancies/{id}/resolve` and emergency control endpoints.

## Consequences & Trade-Offs
* **Benefits**: Prevents unauthorized users or agents from invoking admin commands.
* **Trade-Offs**: Requires step-up authentication for administrative operators.
