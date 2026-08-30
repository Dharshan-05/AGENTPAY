# AGENTPAY Inventory Schema Architecture (Phase 044)

## Executive Summary

This document formalizes the architectural specification and schema layout for `inventory` in **AGENTPAY** (`Phase 044`).

`inventory` maintains current product stock state, reserved quantities, available quantities, and reorder parameters.

---

## 1. Schema Specifications (`inventory`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_inventory)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_inventory_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_product_id)`, `UNIQUE (uq_inventory_tenant_id_product_id)` | Foreign key referencing products |
| `quantity` | `NUMERIC(18,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (quantity >= 0)` | Physical stock quantity |
| `reserved_quantity` | `NUMERIC(18,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (reserved_quantity >= 0)` | Reserved stock quantity |
| `available_quantity` | `NUMERIC(18,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (available_quantity >= 0)` | Available stock quantity |
| `reorder_level` | `NUMERIC(18,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (reorder_level >= 0)` | Reorder threshold quantity |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `CHECK (status IN ('active', 'inactive', 'discontinued'))`, `INDEX (ix_inventory_status)` | Stock status |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Precision Rules

- **NUMERIC Precision**: All quantities use `NUMERIC(18,3)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Quantity Consistency**: `ck_inventory_quantity_consistency` enforces `reserved_quantity <= quantity`, `available_quantity <= quantity`, and `available_quantity + reserved_quantity <= quantity`.
- **Tenant Isolation**: `inventory.tenant_id == merchants.tenant_id == products.tenant_id`.
- **Product Uniqueness**: `uq_inventory_tenant_id_product_id` ensures one current inventory state per product per tenant.
- **Soft Deletion**: `deleted_at` allows soft deletion of obsolete inventory records.
