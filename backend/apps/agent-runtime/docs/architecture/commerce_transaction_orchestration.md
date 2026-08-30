# AGENTPAY Architecture Specification: Phase 184 — Commerce Transaction Orchestration

## Overview
Phase 184 implements `CommerceTransactionOrchestratorService`, providing end-to-end execution orchestration for purchase requests without duplicating existing payment engine logic.

## Orchestration Pipeline & Invariants
- **Execution Pipeline**: `Purchase Request -> Commerce Validation -> Authorization -> Approval Policy Check -> Idempotency Protection -> AgentPay Financial Initiation`.
- **Deterministic State Machine**:
  - `VALIDATING` -> `AUTHORIZED` -> `PENDING_APPROVAL` / `READY_FOR_EXECUTION` -> `EXECUTING` -> `COMPLETED` (or `FAILED` / `CANCELLED`).
- **No Payment Engine Duplication**: Delegates financial transaction initiation to `AgentPayToolAdapter.initiate_payment` and `AgentTransactionOrchestratorService`.
- **Anti-Self-Approval Enforcement**: Preserves `HumanApprovalWorkflowService` security rules.
- **Post-Completion Cancellation Prevention**: Rejects cancellation attempts for transactions in `COMPLETED` state (`ExecutionValidationError`).

## REST APIs
- `POST /api/v1/purchase-requests/{request_id}/execute`
- `GET /api/v1/purchase-requests/{request_id}/execution`
- `POST /api/v1/purchase-requests/{request_id}/cancel`
