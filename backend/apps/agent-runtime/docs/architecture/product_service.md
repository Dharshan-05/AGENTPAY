# AGENTPAY Architecture Specification: Phase 164 — Product Service

## Overview
Phase 164 establishes the Product domain service in AGENTPAY's Commerce Engine, managing product lifecycles and business invariants.

## Domain Model Reuse
Reuses the pre-existing `Product` ORM entity in [`app/infrastructure/database/models/product.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/product.py) mapped to the `products` table.

## Key Rules & Invariants
1. **Monetary Precision**: Uses `Decimal(12, 2)` (`Numeric(12, 2)`). Zero float/real types. Prices must be `> Decimal("0.00")`.
2. **Tenant & Merchant Ownership**: Enforces `tenant_id` isolation. Validates target `merchant_id` belongs to requesting tenant.
3. **SKU Uniqueness**: Enforced per merchant (`tenant_id` + `merchant_id` + `sku`).
4. **Lifecycle States**: `ACTIVE`, `INACTIVE`, `ARCHIVED`, `DISCONTINUED`.
