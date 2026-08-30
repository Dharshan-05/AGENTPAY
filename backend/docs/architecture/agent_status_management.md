# Phase 130 — Agent Status Management Architecture

## Overview
Phase 130 provides a centralized, controlled API for querying and managing agent operational status while delegating all lifecycle state transitions strictly to `AgentLifecycleService`.

## Architectural Invariants
- **No Duplicate State Machine**: All status transitions MUST call `AgentLifecycleService.validate_transition()` and `AgentLifecycleService.update_agent_status()`. Routers never mutate `agents.status` directly.
- **Fail-Closed State Machine Rules**:
  - `provisioning` $\rightarrow$ `active`, `suspended`, `deactivated`
  - `active` $\rightarrow$ `paused`, `suspended`, `deactivated`
  - `paused` $\rightarrow$ `active`, `suspended`, `deactivated`
  - `suspended` $\rightarrow$ `active`, `deactivated`
  - `deactivated` $\rightarrow$ $\emptyset$ (Strictly terminal! Resurrecting deactivated agent fails closed!)
- **Session Integration**: Pausing (`status="paused"`) or suspending or deactivating an agent automatically revokes active agent sessions (`status="revoked"`). Resuming an agent does NOT automatically recreate sessions.
- **Credential Requirement**: Resuming/activating an agent requires an active credential (`status="active"`) to exist.
- **IDOR Protection**: Every query is tenant-isolated: `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant status requests return `HTTP 404 Not Found` (`AgentNotFoundError`).

## Authorization Matrix
| Method | Path | Permission Required | Description |
|---|---|---|---|
| GET | `/api/v1/agents/{agent_id}/status` | `agents:status_read` | Get agent operational status & lifecycle metadata |
| PATCH | `/api/v1/agents/{agent_id}/status` | `agents:status_update` | Controlled status update dispatcher |
| POST | `/api/v1/agents/{agent_id}/pause` | `agents:pause` | Pause active agent and revoke active sessions |
| POST | `/api/v1/agents/{agent_id}/resume` | `agents:resume` | Resume paused agent back to active status |
