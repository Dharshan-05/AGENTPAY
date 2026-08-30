# AGENTGUARD Architecture Specification: Phase 183 — Agent Authorization

## Overview
Phase 183 implements `AgentAuthorizationService`, determining whether an authenticated principal is authorized to perform an operation on behalf of a verified agent.

## Integration & Boundary Rules
- **Core RBAC Reuse**: Reuses `AuthorizationService` and permission registry (`ALL_PERMISSIONS`). Does NOT create a parallel RBAC or permission engine.
- **Identity Prerequisite**: Executes `AgentIdentityVerificationService` as the mandatory first step. If identity is unverified or inactive, returns `allowed = False` (`IDENTITY_NOT_VERIFIED`).
- **Effective Permission Resolution**: Combines effective agent permissions (`resolve_agent_permissions`) and user principal permissions (`resolve_permissions`).
- **Deterministic Decision**: Returns `allowed: bool` with safe, non-sensitive `decision_reason`.
- **Permission Enforcement**: `require_agent_permission` method raises `PermissionDeniedError` if authorization fails.

## REST API
- `POST /api/v1/agents/{agent_id}/authorization/check`
