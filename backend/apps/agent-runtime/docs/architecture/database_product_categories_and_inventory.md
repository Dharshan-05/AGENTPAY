# AGENTPAY Product Categories and Inventory Architecture (Phase 043 & Phase 044)

## Executive Summary

This document formalizes the architectural specification, schema layout, and operational constraints for `product_categories` (**Phase 043**) and `inventory` (**Phase 044**) in **AGENTPAY** (`apps/agent-runtime`).

---

## 1. Product Categories Schema (`product_categories`)

`product_categories` represents a hierarchical product taxonomy owned by a merchant within a tenant boundary.

### 1.1 Table Schema Layout

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_product_categories)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_product_categories_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_product_categories_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_product_categories_merchant_id)` | Foreign key referencing merchants |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Category display name |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_product_categories_tenant_id_merchant_id_slug)` | Tenant and merchant-scoped unique slug |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Optional description |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_product_categories_status)` | Category operational status (`active`, `inactive`, `archived`) |
| `parent_category_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_product_categories_parent_category_id_product_categories) REFERENCES product_categories(id) ON DELETE RESTRICT`, `INDEX (ix_product_categories_parent_category_id)` | Self-referencing parent category |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-sensitive operational metadata |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

### 1.2 Category Constraints
- **Uniqueness**: `uq_product_categories_tenant_id_merchant_id_slug` enforces unique slugs within `(tenant_id, merchant_id, slug)`.
- **No Self-Parenting**: Check constraint `ck_product_categories_no_self_parent` enforces `parent_category_id IS NULL OR parent_category_id <> id`.

---

## 2. Inventory Schema (`inventory`)

`inventory` represents the current stock state and reordering parameters for a product belonging to a merchant within a tenant boundary.

### 2.1 Table Schema Layout

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_inventory)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_inventory_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_product_id)`, `UNIQUE (uq_inventory_tenant_id_product_id)` | Foreign key referencing products |
| `quantity` | `NUMERIC(12,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (quantity >= 0)` | Physical stock quantity |
| `reserved_quantity` | `NUMERIC(12,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (reserved_quantity >= 0)`, `CHECK (reserved_quantity <= quantity)` | Reserved stock quantity |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'available'`, `INDEX (ix_inventory_status)` | Stock status (`available`, `low_stock`, `out_of_stock`, `disabled`) |
| `location_code` | `VARCHAR(100)`| `NULLABLE` | — | Operational warehouse location code |
| `reorder_level` | `NUMERIC(12,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (reorder_level >= 0)` | Threshold quantity for automated reorders |
| `reorder_quantity` | `NUMERIC(12,3)`| `NOT NULL` | `DEFAULT 0.000`, `CHECK (reorder_quantity >= 0)` | Target quantity for automated reorders |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-sensitive operational metadata |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

### 2.2 Quantity & Precision Standards
- **NUMERIC Precision**: `quantity`, `reserved_quantity`, `reorder_level`, and `reorder_quantity` use `NUMERIC(12,3)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED for inventory quantities.
- **Check Constraints**:
  - `ck_inventory_quantity_nonnegative`: `quantity >= 0`
  - `ck_inventory_reserved_quantity_nonnegative`: `reserved_quantity >= 0`
  - `ck_inventory_reserved_quantity_lte_quantity`: `reserved_quantity <= quantity`
  - `ck_inventory_reorder_level_nonnegative`: `reorder_level >= 0`
  - `ck_inventory_reorder_quantity_nonnegative`: `reorder_quantity >= 0`

---

## 3. Tenant Isolation & Security Boundaries

- **Tenant Isolation Invariant**:
  - `product_category.tenant_id == merchant.tenant_id`
  - `inventory.tenant_id == merchant.tenant_id == product.tenant_id`
- **Zero Secrets Policy**: Credentials, tokens, private keys, or passwords MUST NOT be stored in `product_categories` or `inventory`.
- **Repr Safety**: `metadata_payload` fields are explicitly excluded from `__repr__` output across all models.
