# Agent Transaction Orchestration Architecture (Phase 161)

## Overview
The Agent Transaction Orchestration subsystem coordinates multi-step agent-driven payment workflows, tool calls, and state transitions in AGENTPAY.

## Lifecycle States
```text
CREATED
  ↓
VALIDATING
  ↓
AUTHORIZED
  ↓
PENDING_APPROVAL
  ↓
EXECUTING
  ↓
PROCESSING
  ↓
COMPLETED
```

Failure & Terminal States:
- `FAILED`
- `CANCELLED`
- `EXPIRED`
- `REJECTED`

## Key Capabilities
- **Step Execution Modes**: `SEQUENTIAL`, `PARALLEL`, `CONDITIONAL`.
- **State Persistence**: Workflow execution states stored in `PurchasePlan` metadata with strict tenant isolation.
- **Idempotency Propagation**: Transaction correlation across `idempotency_key`, `workflow_id`, `agent_id`, and `tenant_id`.
