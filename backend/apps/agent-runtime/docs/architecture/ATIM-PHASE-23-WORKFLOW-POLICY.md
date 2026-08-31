# ATIM Phase 23 — Durable Workflow Orchestration Policy

## 1. Core Workflow Execution Rules
1. **ZERO LLM WORKFLOW AUTHORITY**: Workflow state transitions and step completions **MUST NEVER** be controlled by unvalidated LLM output or user prompts. Server-side validation is authoritative.
2. **STEP-LEVEL IDEMPOTENCY**: Executing a workflow step `(workflow_id, step_index)` multiple times must be idempotent. Re-executing a completed step returns the saved step result.
3. **DECISION PRECEDENCE INTEGRITY**: A security block or AgentGuard denial during any step immediately transitions the workflow instance to `FAILED`.
4. **CRYPTOGRAPHIC COMPLIANCE EVIDENCE**: All workflow state changes (instance creation, step completion, failure, cancellation) generate SHA-256 HMAC cryptographic audit signatures via `ATIMAuditLockService`.
