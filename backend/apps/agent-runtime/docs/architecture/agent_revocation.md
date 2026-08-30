# Agent Revocation Architecture (Phase 126)

## Overview

Phase 126 implements permanent agent revocation (deactivation). Deactivation permanently disables an autonomous agent from performing any further operations while preserving immutable audit logs and historical references.

## API Endpoint

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/revoke` | `agents:revoke` | Permanently revoke/deactivate an agent |

## State Machine Transition

```
ACTIVE ("active") → DEACTIVATED ("deactivated")
SUSPENDED ("suspended") → DEACTIVATED ("deactivated")
PAUSED ("paused") → DEACTIVATED ("deactivated")
PROVISIONING ("provisioning") → DEACTIVATED ("deactivated")
```

**TERMINAL STATE RULE**: `DEACTIVATED` is a strictly terminal state. No transitions out of `deactivated` status are permitted by `validate_transition()`.

Attempting to revoke an agent that is already deactivated raises `AgentAlreadyRevokedError` (`HTTP 409 Conflict`).

## Execution Workflow & Atomic Effects

1. **Authorization & Tenant Isolation**: Scoped by `WHERE id = :agent_id AND tenant_id = :tenant_id`. Requires `agents:revoke`.
2. **Atomic Transaction**:
   - `agents.status` updated to `"deactivated"`
   - `agent_lifecycle.status` updated to `"deactivated"`
   - `agent_lifecycle.deactivated_at` recorded as `datetime.now(UTC)`
   - All active sessions belonging to the agent are revoked (`status="revoked"`)
   - All active credentials belonging to the agent are invalidated (`status="revoked"`, `revoked_at=now`)
3. **Zero Hard Deletion**: The agent entity, identity, credential metadata, and lifecycle records remain persisted for audit tracking.
