# Agent Suspension Architecture (Phase 125)

## Overview

Phase 125 implements production-grade agent suspension, allowing an authorized operator to temporarily disable an active agent while preserving all historical data, identity profiles, and audit records.

## API Endpoint

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/suspend` | `agents:suspend` | Suspend active agent & revoke active sessions |

## State Machine Transition

```
ACTIVE ("active") → SUSPENDED ("suspended")
PROVISIONING ("provisioning") → SUSPENDED ("suspended")
PAUSED ("paused") → SUSPENDED ("suspended")
```

Attempting to suspend an already suspended agent raises `AgentAlreadySuspendedError` (`HTTP 409 Conflict`).
Attempting to suspend a deactivated agent raises `InvalidAgentLifecycleTransitionError` (`HTTP 400 Bad Request`).

## Execution Workflow

1. **Authorization & Tenant Context**: Extracted strictly from JWT principal (`current_user.tenant_id`). Permission check `require_permission(AGENTS_SUSPEND)` enforced via FastAPI dependency.
2. **Tenant IDOR Lookup**: Query checks `WHERE id = :agent_id AND tenant_id = :tenant_id`. Cross-tenant requests return `HTTP 404 Not Found` (`AgentNotFoundError`).
3. **Atomic State Mutation**:
   - `agents.status` updated to `"suspended"`
   - `agent_lifecycle.status` updated to `"suspended"`
   - `agent_lifecycle.suspended_at` recorded as `datetime.now(UTC)`
   - `agent_lifecycle.last_transition_at` updated
4. **Session Invalidation Integration**: All active sessions belonging to the suspended agent are revoked atomically (`status="revoked"`, `revocation_reason="Agent suspended"`).
5. **Credential Preserved**: Historical credential metadata remains intact in `agent_credentials`, but credential authentication and session creation attempts for suspended agents fail closed.
