# Phase 129 — Agent Role Assignment Architecture

## Overview
Phase 129 implements role assignment for autonomous agents in AGENTPAY. Agents can be assigned tenant-scoped roles or immutable system roles.

## Architectural Invariants
- **Existing RBAC Reuse**: Reuses `Role`, `AgentRole`, `RolePermission`, `UserRole`, and `AuthorizationService`.
- **Tenant Scope & System Role Rules**: An agent can only be assigned roles belonging to its `tenant_id` or global system roles (`is_system=True`).
- **IDOR Protection**: All operations check `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant lookup returns `HTTP 404 Not Found` (`AgentNotFoundError`).
- **Duplicate Prevention**: Database unique constraint `uq_agent_roles_agent_id_role_id` prevents duplicate assignments, raising `AgentRoleAlreadyAssignedError` (`HTTP 409 Conflict`).
- **System Role Preservation**: System roles (`is_system=True`) are immutable definitions; revoking an agent-role assignment deletes the link in `agent_roles` without modifying the `Role` definition.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/roles` | `agents:roles_read` | List assigned roles for agent |
| POST | `/api/v1/agents/{agent_id}/roles` | `agents:roles_assign` | Assign tenant/system role to agent |
| DELETE | `/api/v1/agents/{agent_id}/roles/{role_id}` | `agents:roles_revoke` | Revoke role assignment from agent |
