# AGENTPAY Product Categories Schema Architecture (Phase 043)

## Executive Summary

This document formalizes the architectural specification and schema layout for `product_categories` in **AGENTPAY** (`Phase 043`).

`product_categories` provides tenant-isolated hierarchical product categorization owned by merchants within a multi-tenant boundary.

---

## 1. Schema Specifications (`product_categories`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_product_categories)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_product_categories_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_product_categories_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_product_categories_merchant_id)` | Foreign key referencing merchants |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Category display name |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_product_categories_tenant_id_slug)` | Tenant-scoped unique slug |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Category description |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `CHECK (status IN ('active', 'inactive', 'archived'))`, `INDEX (ix_product_categories_status)` | Operational status |
| `parent_category_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_product_categories_parent_category_id_product_categories) REFERENCES product_categories(id) ON DELETE RESTRICT`, `INDEX (ix_product_categories_parent_category_id)` | Self-referencing parent category |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `product_categories.tenant_id == merchants.tenant_id`.
- **Tenant-Scoped Slug Uniqueness**: `uq_product_categories_tenant_id_slug` ensures uniqueness per tenant.
- **No Self-Parenting**: Check constraint `ck_product_categories_parent_not_self` prevents `parent_category_id == id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent categories while child categories exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, or private keys MUST NOT be stored.
