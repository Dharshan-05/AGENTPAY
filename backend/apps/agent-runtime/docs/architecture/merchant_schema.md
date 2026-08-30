# AGENTPAY Merchant Schema Architecture (Phase 041)

## Executive Summary

This document formalizes the architectural specification and schema layout for the commercial merchant entity table `merchants` in **AGENTPAY** (`Phase 041`).

`merchants` represents a tenant-owned commercial business entity that offers products and participates in AGENTPAY commerce operations.

---

## 1. Table Schema Layout (`merchants`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_merchants)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_merchants_tenant_id)` | Multi-tenancy isolation key |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Display/business name of the merchant |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_merchants_tenant_id_slug)` | Tenant-scoped unique slug identifier |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_merchants_status)` | Operational status (`active`, `inactive`, `suspended`) |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Merchant description |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Security & Constraints

- **Tenant Isolation**: `merchants.tenant_id` guarantees multi-tenant merchant partitioning.
- **Tenant-Scoped Slug Uniqueness**: Constraint `uq_merchants_tenant_id_slug` ensures `(tenant_id, slug)` uniqueness. Different tenants may use identical slugs.
- **Soft Deletion**: Standard `deleted_at` column preserves audit history upon deletion.
- **Zero Credentials**: Passwords, API keys, bearer tokens, or payment secrets are NEVER stored on the Merchant entity.
