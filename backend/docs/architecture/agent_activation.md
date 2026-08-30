# Agent Activation (Phase 124)

## Overview

Phase 124 exposes the production-grade API endpoint for activating an autonomous agent from `provisioning` to `active` operational state.

## API Endpoint

| Method | Path | Authorization | Purpose |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/activate` | `agents:activate` | Transition agent to active operational state |

## Execution Workflow

```
POST /api/v1/agents/{agent_id}/activate
  → require_permission(AGENTS_ACTIVATE)
  → AgentLifecycleService.activate_agent()
  → 1. Tenant-scoped IDOR check: WHERE id = :agent_id AND tenant_id = :tenant_id
  → 2. Already active check: Raise AgentAlreadyActiveError if status == "active"
  → 3. State machine validation: Check provisioning -> active transition
  → 4. Credential dependency check: Verify agent has >= 1 active AgentCredential
  → 5. Atomic DB update: Update agents.status = 'active' and agent_lifecycle.status = 'active'
```

## Security & Interaction Controls

1. **Credential Requirement**: Before activation can occur, an agent MUST have an active credential issued via Phase 122 (`POST /api/v1/agents/{agent_id}/credentials`). If no active credential exists, activation is rejected with `AgentActivationError`.
2. **Tenant Isolation & IDOR Protection**: Scoped by `WHERE id = :agent_id AND tenant_id = :authenticated_tenant_id`. Cross-tenant requests raise `AgentNotFoundError` (`HTTP 404 Not Found`).
3. **Already Active Conflict**: Attempting to activate an agent that is already active raises `AgentAlreadyActiveError` (`HTTP 409 Conflict`).
4. **Atomic State Mutation**: `agents.status` and `agent_lifecycle.status` are updated atomically in the same database transaction.
