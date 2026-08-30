# Phase 150 — Agent State Management Architecture

## Overview

**Agent State Management** (`AgentStateService`) manages the runtime state representation and transition state machine for agents in AGENTPAY. It operates separately from authoritative agent lifecycle status (`active`, `paused`, `suspended`, `deactivated`), maintaining explicit runtime state machine rules.

---

## Canonical Runtime States

- `IDLE`: Initial idle state.
- `PREPARING`: Preparing orchestration parameters.
- `READY`: Ready for downstream execution (Phase 151+).
- `BLOCKED`: Blocked due to operational or policy constraints.
- `WAITING`: Awaiting authorization or external event.
- `FAILED`: Orchestration/state validation failure.
- `CANCELLED`: User or system cancelled.

> [!WARNING]
> **PROHIBITED STATES**
> `EXECUTING`, `TOOL_EXECUTING`, and `PAYMENT_EXECUTING` states are **prohibited** in Phase 150 and strictly belong to Phase 151+.

---

## Explicit State Transition Graph

- `IDLE` $\rightarrow$ `PREPARING`
- `PREPARING` $\rightarrow$ `READY` | `BLOCKED` | `FAILED`
- `READY` $\rightarrow$ `WAITING` | `CANCELLED`
- `WAITING` $\rightarrow$ `READY` | `BLOCKED`
- `BLOCKED` $\rightarrow$ `READY`
- `FAILED` $\rightarrow$ `IDLE`
- `CANCELLED` $\rightarrow$ `IDLE`

Attempting any transition outside this explicit state machine raises `InvalidAgentStateTransitionError`.

---

## Agent Lifecycle Integration

- **DEACTIVATED / REVOKED**: State updates are rejected fail-closed.
- **SUSPENDED**: State is forced to `BLOCKED`.
- **PROVISIONING**: State cannot become `READY`.

---

## API Endpoints

- `GET /api/v1/agents/{agent_id}/state` (`agents:state_read`)
- `PATCH /api/v1/agents/{agent_id}/state` (`agents:state_update`)
