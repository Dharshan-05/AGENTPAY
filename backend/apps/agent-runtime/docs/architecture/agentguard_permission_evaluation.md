# AGENTGUARD Architecture Specification: Phase 184 — Agent Permission Evaluation

## Overview
Phase 184 implements `AgentPermissionEvaluationService`, resolving the effective permissions available to an agent for requested operations.

## Evaluation Semantics & Boundaries
- **Permission Availability Focus**: Evaluates permission availability only. Does NOT evaluate spending limits, category/merchant restrictions, or time-based policy rules (reserved for Phase 185+).
- **Effective Grant Calculation**: Resolves combined grants from `AuthorizationService` (direct agent permissions + inherited role permissions + user principal permissions).
- **Multi-Permission Evaluation**: Evaluates lists of requested permissions. Returns explicit `granted_permissions` and `missing_permissions`.
- **Deterministic Reason Codes**:
  - `PERMISSION_GRANTED`: All requested permissions satisfied (`decision = "GRANTED"`).
  - `PERMISSION_MISSING`: One or more permissions missing (`decision = "DENIED"`).
  - `IDENTITY_NOT_VERIFIED`: Agent unverified or inactive (`decision = "DENIED"`).

## REST APIs
- `POST /api/v1/agents/{agent_id}/permissions/evaluate`
- `GET /api/v1/agents/{agent_id}/permissions/effective`
