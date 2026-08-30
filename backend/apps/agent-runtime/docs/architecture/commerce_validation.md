# AGENTPAY Architecture Specification: Phase 182 — Commerce Validation

## Overview
Phase 182 implements an authoritative, centralized commerce validation layer (`CommerceValidationService`) that validates complete purchase request contexts prior to transaction execution.

## Deterministic Validation Order
1. Authenticated tenant resolution and isolation verification.
2. Purchase Request lookup (`PurchaseIntent` entity).
3. Request terminal state check (`pending`, `approved` vs terminal `rejected`, `expired`, `cancelled`).
4. Parent `PurchasePlan` resolution.
5. Product status check (`Product.status == "active"`).
6. Advisory Stock Revalidation (`InventoryValidationService.validate_inventory`).
7. Offer Optimization Revalidation (`OfferOptimizationService.optimize_offer`).
8. Stale Pricing / Plan Detection: compares snapshot pricing against current revalidated total. If price differs by `> Decimal('0.0100')`, returns `valid = false` with error `PRICE_CHANGED`.
9. Single Currency consistency check.
10. Human Approval Policy check (`HumanApprovalWorkflowService.evaluate_approval_policy`).

## REST API
- `POST /api/v1/purchase-requests/{request_id}/validate`
