# AGENTPAY Architecture Specification: Phase 181 — Purchase Request

## Overview
Phase 181 implements pre-execution purchase request handling (`PurchaseRequestService`) and approval integration.

## Revalidation & Pre-Execution Boundary
- **ORM Reuse**: Reuses pre-existing `PurchaseIntent` ORM entity in [`app/infrastructure/database/models/purchase_intent.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/purchase_intent.py). Zero duplicate ORM entities created.
- **Stale Plan Revalidation**: Revalidates current stock availability and pricing against the plan snapshot. If pricing or stock differs, returns `REPLAN_REQUIRED` without executing.
- **Approval Integration**: Reuses `HumanApprovalWorkflowService`. If plan total >= $500 threshold, sets `status = "PENDING_APPROVAL"`, `requires_approval = True`. Anti-self-approval security is preserved.
- **Pre-Execution Guarantee**: Purely creates pre-execution intent records. Does NOT charge cards, debit wallets, transfer money, or reserve/deduct stock.
- **REST Endpoints**: `POST /api/v1/purchase-requests` and `GET /api/v1/purchase-requests/{request_id}`.
