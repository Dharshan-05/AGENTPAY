# AGENTPAY Architecture Specification: Phase 176 — Inventory Check

## Overview
Phase 176 establishes the read-only inventory availability check service (`InventoryCheckService`) in AGENTPAY's Commerce Engine.

## Model Reuse & Invariants
- **ORM Reuse**: Reuses pre-existing `Inventory` ORM entity in [`app/infrastructure/database/models/inventory.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/inventory.py) mapped to `inventory` table. Zero duplicate ORM entities created.
- **Quantity Validation**: `requested_quantity` must be strictly `> Decimal("0.000")`. Rejects non-positive or non-numeric input.
- **Availability States**: `AVAILABLE` (`available_quantity >= requested_quantity`), `PARTIALLY_AVAILABLE` (`0 < available_quantity < requested_quantity`), `UNAVAILABLE` (`available_quantity <= 0`), `UNKNOWN` (unstocked item; zero fabrication of stock numbers).
- **Tenant Isolation**: Strictly tenant-scoped (`tenant_id = :authenticated_tenant`).
- **REST Endpoint**: `GET /api/v1/products/{product_id}/inventory?quantity=1`.
