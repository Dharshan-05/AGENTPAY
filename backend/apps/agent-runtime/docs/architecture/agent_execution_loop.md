# Phase 151 — Agent Execution Loop Architecture

## Overview

The **Agent Execution Loop** (`AgentExecutionService`) provides a production-grade step-by-step execution progression engine for the AGENTPAY platform. It takes a validated purchase plan (`AgentPlan`) and orchestration decision (`AgentOrchestrationResponse`), verifies execution eligibility, and manages step progression, bounded retries, state machine integration, and controlled execution boundaries.

> [!IMPORTANT]
> **STRICT EXECUTION BOUNDARY**
> Phase 151 introduces the execution loop progression framework. It does **NOT** implement arbitrary tool execution, shell/subprocess execution, or external payment provider calls. Any step requiring external tool execution frameworks (Phase 156+) is safely caught at the boundary, returning `UNSUPPORTED_EXECUTION_BOUNDARY` with status `BLOCKED`.

---

## Canonical Execution Taxonomy

- `CREATED`: Execution loop initialized.
- `VALIDATING`: Validating plan, orchestration, and agent eligibility.
- `READY`: Execution loop ready to progress.
- `EXECUTING`: Progression loop actively running steps.
- `STEP_RUNNING`: Individual step running.
- `RETRYING`: Retrying transient step failure.
- `COMPLETED`: All executable steps completed successfully.
- `FAILED`: Execution step failed terminally or exceeded retry policy limits.
- `BLOCKED`: Execution stopped at an unsupported tool boundary or policy restriction.
- `CANCELLED`: User or system cancelled execution loop.

---

## Execution Loop Invariants & Controls

1. **Strict Tenant Isolation**: All database operations enforce `WHERE agent_id = :agent_id AND tenant_id = :authenticated_tenant_id`. Client tenant overrides are strictly forbidden (`extra="forbid"`).
2. **IDOR Defense**: Cross-tenant attempts return `HTTP 404 Not Found` (`ExecutionNotFoundError` / `AgentNotFoundError`).
3. **Pre-execution Verification**:
   - `Agent.status` must be `active` (not `paused`, `suspended`, `revoked`, `deactivated`).
   - Plan must be valid (`is_valid = True`, `execution_eligible = True`).
   - Orchestration decision must be `READY`.
   - `UNKNOWN` intent category is strictly forbidden (`ExecutionPolicyViolationError`).
4. **Bounded Retries**: Step failures are retried up to `retry_policy.max_attempts`. Non-retryable errors fail immediately.
5. **Runtime State Integration**: Updates `AgentStateService` runtime state machine (`IDLE` $\rightarrow$ `PREPARING` $\rightarrow$ `READY` $\rightarrow$ `WAITING` / `IDLE`).
6. **Audit & Security Logging**: Emits `execution_created`, `execution_started`, `execution_completed`, `execution_failed`, and `execution_cancelled` audit events.

---

## REST API Endpoints

- `POST /api/v1/agents/{agent_id}/executions` (`agents:execute`)
- `GET /api/v1/agents/{agent_id}/executions/{execution_id}` (`agents:execution_read`)
- `POST /api/v1/agents/{agent_id}/executions/{execution_id}/cancel` (`agents:execution_cancel`)
