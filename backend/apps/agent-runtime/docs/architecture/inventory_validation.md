# AGENTPAY Architecture Specification: Phase 177 — Inventory Validation

## Overview
Phase 177 establishes a read-only advisory inventory validation layer (`InventoryValidationService`) for single and bulk purchase requests.

## Advisory Validation Rules & Bounds
- **Read-Only Advisory**: Purely advisory check (`valid: bool`). Performs zero stock reservation, zero stock locks, and zero stock deductions.
- **Bulk Validation Bounds**: Allows single product validation or bounded bulk validation up to 50 items (`items <= 50`).
- **Validation Reasons**: `VALID`, `PRODUCT_NOT_FOUND`, `PRODUCT_INACTIVE`, `INSUFFICIENT_STOCK`, `INVENTORY_UNKNOWN`, `INVALID_QUANTITY`.
- **Tenant Security**: Enforces tenant-scoped checking for all requested product UUIDs. Cross-tenant products return fail-closed validation results.
- **REST Endpoint**: `POST /api/v1/products/inventory/validate`.
