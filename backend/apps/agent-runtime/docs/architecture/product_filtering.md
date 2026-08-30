# AGENTPAY Architecture Specification: Phase 170 — Product Filtering

## Overview
Phase 170 implements database-driven product filtering in AGENTPAY's Commerce Engine.

## Filtering Architecture & Supported Filters
All filtering takes place inside the database engine (`WHERE tenant_id = :tenant_id AND ...`):
- `merchant_id`: Parent merchant UUID filter.
- `status`: Lifecycle status filter (`active`, `inactive`, `archived`, `discontinued`).
- `currency`: ISO 4217 currency code filter (e.g. `USD`).
- `min_price` / `max_price`: Financial price bounds using `Decimal(12, 2)`. Validated `min_price >= 0`, `max_price >= 0`, `min_price <= max_price`.
- `created_after` / `created_before`: Datetime range filters.

## Invariants & Security
- **Tenant Isolation**: Strictly enforced at repository level (`tenant_id = :authenticated_tenant`).
- **Soft Deletion**: Excludes soft-deleted records (`deleted_at IS NULL`).
