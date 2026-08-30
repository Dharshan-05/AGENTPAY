# Agent Lifecycle Service (Phase 123)

## Overview

Phase 123 implements a centralized domain service (`AgentLifecycleService`) that models agent runtime state transitions as an explicit finite state machine.

## State Machine Architecture

```
PROVISIONING ("provisioning")
     ↓ (Phase 124 Activation)
ACTIVE ("active")
     ↓
PAUSED / SUSPENDED / DEACTIVATED (Future Phase Boundaries)
```

## Transition Rules Matrix

| Current State | Target State | Legal? | Trigger |
|---|---|---|---|
| `provisioning` | `active` | **YES** | Agent Activation API (`POST /activate`) |
| `provisioning` | `paused` / `suspended` / `deactivated` | **NO** | Must activate first |
| `active` | `paused` | **YES** | Agent Pause (Phase 125+) |
| `active` | `suspended` | **YES** | Agent Suspension (Phase 125+) |
| `active` | `deactivated` | **YES** | Agent Revocation (Phase 126+) |
| `paused` | `active` / `deactivated` | **YES** | Resume / Deactivate |
| `suspended` | `active` / `deactivated` | **YES** | Unsuspend / Deactivate |
| `deactivated` | *any state* | **NO** | Terminal state |

## Database Integration

Reused existing `agent_lifecycle` table (migration `009_agent_lifecycle_and_metadata.py`):
- `id`: UUIDv7 primary key
- `tenant_id`: Multi-tenancy isolation key (indexed)
- `agent_id`: FK → `agents.id` (1-to-1 unique constraint)
- `status`: Current status string (`'provisioning'`, `'active'`, etc.)
- `status_reason`: Human-readable status reason
- `activated_at`: Timestamp of activation
- `last_transition_at`: Timestamp of last transition

## Security & Fail-Closed Rules

- Invalid state transitions raise `InvalidAgentLifecycleTransitionError`.
- All queries enforce tenant isolation (`WHERE tenant_id = :tenant_id`).
- State updates mutate both `agents.status` and `agent_lifecycle.status` within the same database transaction.
