# AGENTPAY Architecture Specification: Phase 156 — Tool Calling Framework

## Overview
Phase 156 establishes a production-grade, strongly-typed execution environment for agent tool calls in AGENTPAY.

## Deterministic Execution State Machine
```
REQUESTED ──> VALIDATING ──> AUTHORIZED ──> EXECUTING ──> SUCCEEDED
                                               │
                                               ├──> FAILED
                                               ├──> TIMEOUT
                                               ├──> CANCELLED
                                               └──> REJECTED
```

## Security & Reliability Gates
1. **Input Schema Gate**: Validates arguments against registered JSON schema definitions.
2. **Permission Gate (Phase 158)**: Enforces RBAC permissions (`agents:execute`).
3. **Idempotency & Financial Safety Gate**: Mandates `idempotency_key` for high-risk/critical operations.
4. **Audit Logger Gate (Phase 159)**: Emits immutable audit records for execution telemetry.

## API Endpoints
- `POST /api/v1/agents/{agent_id}/tools/execute` (requires `agents:execute`)
