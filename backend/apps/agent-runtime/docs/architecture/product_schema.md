# AGENTPAY Product Schema Architecture (Phase 042)

## Executive Summary

This document formalizes the architectural specification and schema layout for the commercial product table `products` in **AGENTPAY** (`Phase 042`).

`products` represents a commercial product item offered by a Merchant with financial precision pricing (`NUMERIC(12,2)`), merchant-scoped SKU uniqueness, and extensible non-sensitive metadata.

---

## 1. Table Schema Layout (`products`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_products)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_products_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_products_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_products_merchant_id)` | Foreign key referencing merchants |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Product display name |
| `sku` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_products_merchant_id_sku)` | Merchant-scoped Stock Keeping Unit |
| `description` | `VARCHAR(1000)`| `NULLABLE` | — | Product detailed description |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_products_status)` | Product status (`active`, `inactive`, `discontinued`) |
| `price` | `NUMERIC(12,2)`| `NOT NULL` | `DEFAULT 0.00`, `CHECK (price >= 0)` | Financial monetary price |
| `currency_code` | `VARCHAR(3)`| `NOT NULL` | `DEFAULT 'USD'` | ISO 4217 currency code |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Extensible non-sensitive product metadata |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Security & Financial Constraints

- **Financial Precision**: `price` MUST be `NUMERIC(12,2)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED for monetary values.
- **Non-Negative Price Protection**: `ck_products_price_nonnegative` enforces `price >= 0`.
- **Merchant Relationship**: Foreign key `fk_products_merchant_id_merchants` enforces `ON DELETE RESTRICT`.
- **Merchant-Scoped SKU Uniqueness**: Constraint `uq_products_merchant_id_sku` ensures `(merchant_id, sku)` uniqueness.
- **Tenant Isolation**: `products.tenant_id == merchants.tenant_id`. Cross-tenant product assignment is strictly REJECTED.
- **Zero Secrets**: `metadata_payload` MUST contain only non-sensitive product attributes. Plaintext credentials are NEVER permitted.
- **Repr Safety**: `metadata_payload` is explicitly excluded from `__repr__` output.
