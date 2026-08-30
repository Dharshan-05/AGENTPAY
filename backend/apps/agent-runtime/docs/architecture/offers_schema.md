# AGENTPAY Offers Schema Architecture (Phase 046)

## Executive Summary

This document formalizes the architectural specification and schema layout for `offers` in **AGENTPAY** (`Phase 046`).

`offers` represents merchant-owned commercial offers that can later be selected by agents during purchase workflows.

---

## 1. Schema Specifications (`offers`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_offers)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_offers_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_offers_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_offers_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_offers_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_offers_product_id)` | Foreign key referencing products |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Commercial offer title |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_offers_tenant_id_slug)` | Tenant-scoped unique slug |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Offer details |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `CHECK (status IN ('active', 'inactive', 'expired', 'suspended'))`, `INDEX (ix_offers_status)` | Offer lifecycle status |
| `price` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (price >= 0)` | Commercial offer price |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | ISO 4217 currency code |
| `starts_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Validity start timestamp |
| `ends_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (starts_at IS NULL OR ends_at IS NULL OR starts_at <= ends_at)` | Validity end timestamp |
| `min_quantity` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 1.000`, `CHECK (min_quantity >= 0)` | Minimum order quantity limit |
| `max_quantity` | `NUMERIC(18,3)` | `NULLABLE` | `CHECK (max_quantity IS NULL OR max_quantity >= min_quantity)` | Maximum order quantity limit |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Metadata payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `offers.tenant_id == merchants.tenant_id == products.tenant_id`.
- **Tenant-Scoped Slug Uniqueness**: `uq_offers_tenant_id_slug` ensures uniqueness per tenant.
- **NUMERIC Precision**: Monetary prices use `NUMERIC(18,4)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent merchants or products while active offers exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, or private keys MUST NOT be stored in `metadata_payload` or exposed in `__repr__`.
