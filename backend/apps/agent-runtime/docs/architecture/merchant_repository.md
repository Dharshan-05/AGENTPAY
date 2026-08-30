# AGENTPAY Architecture Specification: Phase 167 — Merchant Repository

## Overview
Phase 167 establishes the infrastructure data access repository (`MerchantRepository`) for Merchant entities in AGENTPAY's Commerce Engine.

## Domain Model Reuse
Reuses the pre-existing `Merchant` ORM entity in [`app/infrastructure/database/models/merchant.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/merchant.py) mapped to the `merchants` table. Zero duplicate ORM models.

## Repository Responsibilities & Conventions
- Pure data access abstraction decoupled from business logic.
- Strict tenant isolation (`WHERE tenant_id = :tenant_id AND deleted_at IS NULL`).
- Keyset pagination with deterministic ordering (`created_at DESC, id DESC`).
- Methods: `create`, `get_by_id`, `get_by_slug`, `list`, `update`, `archive`, `restore`, `exists`.
