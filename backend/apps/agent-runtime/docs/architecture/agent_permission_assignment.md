# Phase 128 — Agent Permission Assignment Architecture

## Overview
Phase 128 introduces production-grade, tenant-isolated direct permission assignment for autonomous agents in AGENTPAY. Authorized tenant operators/administrators can assign and revoke canonical system permissions to agents.

## Architectural Invariants
- **Single Canonical Registry**: Uses existing `Permission` table and `ALL_PERMISSIONS` registry (`permissions_registry.py`).
- **Tenant Isolation**: Direct assignments stored in `agent_permissions` table (`AgentPermission`), strictly scoped by `tenant_id`.
- **IDOR Protection**: Every query enforces `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant lookup returns `HTTP 404 Not Found` (`AgentNotFoundError`).
- **Duplicate Prevention**: Database unique constraint `uq_agent_permissions_agent_id_permission_id` prevents duplicate assignments, raising `AgentPermissionAlreadyAssignedError` (`HTTP 409 Conflict`).
- **Mass Assignment Protection**: Transport models enforce `extra="forbid"`. Server derives `tenant_id`, `agent_id`, and `permission_id` from route context.

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/permissions` | `agents:permissions_read` | List assigned direct permissions for agent |
| POST | `/api/v1/agents/{agent_id}/permissions` | `agents:permissions_assign` | Assign canonical permission to agent |
| DELETE | `/api/v1/agents/{agent_id}/permissions/{permission_id}` | `agents:permissions_revoke` | Revoke direct permission from agent |

## Effective Permission Resolution
`AuthorizationService.resolve_agent_permissions()` computes the effective permission set for an agent as:
$$\text{Effective Permissions} = \text{Direct AgentPermissions} \cup \text{Role-Inherited Permissions}$$
