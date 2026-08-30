# AGENTPAY Architecture Specification: Phase 165 — Merchant Service

## Overview
Phase 165 establishes the Merchant domain service in AGENTPAY's Commerce Engine, managing commercial merchant entities.

## Domain Model Reuse
Reuses the pre-existing `Merchant` ORM entity in [`app/infrastructure/database/models/merchant.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/merchant.py) mapped to the `merchants` table.

## Key Rules & Invariants
1. **Tenant Isolation**: Every operation is strictly scoped by `tenant_id`.
2. **Slug Uniqueness**: Slugs are generated from business name and enforced unique per tenant (`uq_merchants_tenant_id_slug`).
3. **Lifecycle States**: `ACTIVE`, `INACTIVE`, `SUSPENDED`, `ARCHIVED`.
4. **Merchant-Product Relationship**: Merchants own products (`Merchant 1 ──< Product N`).
