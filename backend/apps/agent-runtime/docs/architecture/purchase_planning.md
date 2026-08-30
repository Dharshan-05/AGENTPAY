# AGENTPAY Architecture Specification: Phase 180 — Purchase Planning

## Overview
Phase 180 establishes the purchase planning subsystem (`PurchasePlanningService`) converting validated items into snapshot purchase plans.

## Pipeline & Invariants
- **ORM Reuse**: Reuses pre-existing `PurchasePlan` ORM entity in [`app/infrastructure/database/models/purchase_plan.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/purchase_plan.py). Zero duplicate ORM entities created.
- **Request Boundaries**: Bounded to 1–50 items. Rejects duplicate product IDs in same plan request.
- **Validation Pipeline**:
  1. Product validation (`ProductRepository`)
  2. Advisory inventory validation (`InventoryValidationService`)
  3. Offer optimization (`OfferOptimizationService`)
  4. Unified currency validation (`currency_code`)
  5. Snapshot creation in `plan_metadata`
- **Idempotency**: Supports replay protection via `idempotency_key`.
- **REST Endpoints**: `POST /api/v1/purchase-plans` and `GET /api/v1/purchase-plans/{plan_id}`.
