# ATIM Group 12 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes industry patterns in durable workflow execution, saga step orchestration, Temporal-style workflow state machines, and fault-tolerant transaction step management to inform **ATIM Group 12 (Phase 23 — ATIM Durable Execution Orchestration & Workflow State Management)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE with ZERO FINANCIAL AUTHORITY**.
- **Durable workflow execution and step orchestration MUST NEVER create a security bypass or allow arbitrary state transitions**.
- **Authoritative Decision Precedence MUST REMAIN**:
  `SECURITY BLOCK > PLAN INVALID > AGENTGUARD DENY > FRAUDGUARD BLOCK > QUOTA DENY > RATE LIMIT DENY > HITL REQUIRED > ALLOW`.

---

## Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **Temporal / Cadence Durable Execution Engine** | Stateful workflow execution, step history recording, atomic state transitions (`INITIATED` $\rightarrow$ `STEP_EXECUTING` $\rightarrow$ `COMPLETED`), deterministic step replaying. | Implement `ATIMWorkflowOrchestrator` service managing workflow instance lifecycle and step history in PostgreSQL. | **ADAPT** | Adopt Temporal-style stateful step execution; REJECT trusting client or LLM input to alter workflow state transitions. |
| **AWS Step Functions / Saga Pattern** | Step-level idempotency, step failure retry policies, step cancellation, step correlation ID tracking. | Implement `ATIMWorkflowStepExecution` ORM entity with `(workflow_id, step_index)` unique constraints. | **ADAPT** | Adopt step-level idempotency; REJECT un-scoped step executions. |
| **Sigstore / SOC 2 Compliance Audit** | Cryptographic evidence generation for workflow state transitions via HMAC-SHA256 signatures. | Integrate workflow transitions with `ATIMComplianceEvidenceService` and `ATIMAuditLockService`. | **ADAPT** | Adopt HMAC-SHA256 evidence logging; REJECT un-signed or mutable workflow audit records. |

---

## Detailed Pattern Decisions

### 1. Durable Workflow State Machine (Phase 23)
- **ADAPT**: Implement `ATIMWorkflowOrchestrator` managing workflow lifecycle states (`INITIATED`, `STEP_EXECUTING`, `STEP_COMPLETED`, `STEP_FAILED`, `WAITING_FOR_APPROVAL`, `CANCELLED`, `COMPLETED`, `FAILED`).
- **REJECT**: Allowing client-supplied `tenant_id` to override server-resolved tenant identity or allowing workflow state mutation without RBAC authorization (`ATIM_POLICY_READ`, `ATIM_SYSTEM_ADMIN`).

### 2. Step History & Cryptographic Evidence (Phase 23)
- **ADAPT**: Step history recording in `atim_workflow_step_executions` table. Produce HMAC-SHA256 signed compliance evidence for all state changes.
- **REJECT**: Deleting or overwriting historical workflow step execution records.
