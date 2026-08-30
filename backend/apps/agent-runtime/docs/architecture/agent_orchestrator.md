# Phase 149 — Agent Orchestrator Architecture

## Overview

The **Agent Orchestrator** (`AgentOrchestratorService`) provides a production-grade orchestration decision engine for the AGENTPAY backend platform. It evaluates stored intent, validated purchase plans, agent lifecycle status, trust posture, and RBAC permissions to produce a canonical orchestration decision representation (`AgentOrchestrationResponse`).

> [!IMPORTANT]
> **CRITICAL ARCHITECTURAL BOUNDARY: ZERO EXECUTION GUARANTEE**
> The Agent Orchestrator operates **strictly** at the preparation boundary. It does **NOT** execute plans, call payment gateways, trigger tool calls, authorize financial transfers, or invoke external provider APIs. Phase 151+ owns execution.

---

## Canonical Orchestration Decision States

- `READY`: All pre-execution checks passed. The agent and plan representation are valid and eligible for future execution.
- `BLOCKED`: A temporary operational condition (e.g. paused status, pending authorization flag, restricted trust posture) prevents progression.
- `REJECTED`: A security violation, deactivated agent status, invalid intent category (`UNKNOWN`), cyclic plan DAG, or cross-tenant IDOR mismatch requires hard rejection.

---

## Canonical Orchestration Lifecycle States

`CREATED` $\rightarrow$ `VALIDATING` $\rightarrow$ `READY` | `BLOCKED` | `REJECTED` | `CANCELLED` | `COMPLETED`

> [!NOTE]
> `COMPLETED` indicates orchestration preparation completion. It does **not** indicate payment or tool execution completion.

---

## Security Boundaries & Controls

1. **Strict Tenant Isolation**: All queries enforce `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Client tenant overrides are forbidden (`extra="forbid"`).
2. **IDOR Defense**: Cross-tenant orchestration access returns `HTTP 404 Not Found` (`AgentNotFoundError`).
3. **Fail-Closed Evaluation**: Any ambiguous or failing rule defaults to `BLOCKED` or `REJECTED`.
4. **Audit & Security Events**: Emits `orchestration_ready`, `orchestration_blocked`, `orchestration_rejected`, and `orchestration_security_rejected` events with zero secret material leakage.

---

## API Endpoints

- `POST /api/v1/agents/{agent_id}/orchestrate` (`agents:orchestrate`)
- `GET /api/v1/agents/{agent_id}/orchestrations/{orchestration_id}` (`agents:orchestration_read`)
