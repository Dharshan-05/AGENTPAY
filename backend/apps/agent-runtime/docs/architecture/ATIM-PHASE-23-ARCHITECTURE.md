# ATIM Phase 23 Architecture — Durable Execution Orchestration & Workflow State Management

## Executive Summary
**ATIM Phase 23 (Group 12)** implements a stateful, durable workflow execution orchestration engine for **AgentPay Transaction Intelligence Model (ATIM)**.

Phase 23 features:
1. **Durable Workflow State Machine (`WorkflowState`)**:
   `INITIATED` $\rightarrow$ `STEP_EXECUTING` $\rightarrow$ `STEP_COMPLETED` $\rightarrow$ `COMPLETED` (or `STEP_FAILED` / `WAITING_FOR_APPROVAL` / `CANCELLED` / `FAILED`).
2. **Step Execution History Recording (`ATIMWorkflowStepExecution`)**: Persists every workflow step attempt, execution status, input/output payload hashes, and timestamps in PostgreSQL table `atim_workflow_step_executions`.
3. **Step-Level Idempotency**: Enforces step-level idempotency key uniqueness `(workflow_id, step_index)` to prevent duplicate step execution during workflow retries or recovery.
4. **Integration with Security Invariants**: Every workflow transition generates a signed HMAC-SHA256 compliance evidence record via `ATIMComplianceEvidenceService`. Security block decisions override workflow continuation immediately.

---

## Durable Workflow State Machine Flow

```text
WORKFLOW INITIATED (State=INITIATED)
          │
          ▼
   EXECUTE STEP N (State=STEP_EXECUTING)
          │
  ├── Step Security Check Passes ──► Execute Step Handler ──► State=STEP_COMPLETED
  ├── Step Security Blocked ──────► State=STEP_FAILED ────► State=FAILED
  └── Step Requires HITL ──────────► State=WAITING_FOR_APPROVAL
          │
          ▼
  All Steps Completed? ──────────► State=COMPLETED
```
