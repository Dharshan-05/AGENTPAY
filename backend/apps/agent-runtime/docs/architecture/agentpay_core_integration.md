# AGENTPAY Architecture Specification: Phase 160 — AgentPay Core Integration

## Overview
Phase 160 establishes a secure boundary adapter (`AgentPayToolAdapter`) connecting agent tool calls to AgentPay core financial interfaces.

## Security & Architectural Boundaries
1. **Zero Direct DB Manipulation**: Agent tools cannot manipulate payment/ledger DB tables directly.
2. **Phase 162 Human Approval Integration**: Financial transactions exceeding $50.00 or sensitive actions (`refund`, `cancel`, `payout`, `transfer`) automatically trigger `HumanApprovalWorkflowService`. Anti-self-approval enforcement is strictly preserved.
3. **Phase 163 Reliability Integration**: Evaluates retry safety classification (`SAFE_TO_RETRY`, `NOT_SAFE_TO_RETRY`, `REQUIRES_RECONCILIATION`) for every operation.
4. **Idempotency Enforcement**: Mandatory idempotency keys (minimum 8 chars) prevent duplicate financial execution.
