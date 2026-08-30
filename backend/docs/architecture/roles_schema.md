# AGENTPAY Roles Schema Architecture (Phase 023)

## Executive Summary

This document formalizes the architectural specification and schema layout for the authorization entity table `roles` in **AGENTPAY** (`Phase 023`).

The `roles` schema supports tenant-scoped custom roles (`tenant_id`), system predefined platform roles (`is_system`), status lifecycle tracking, and audit/soft-deletion capabilities.

---

## 1. Table Schema Layout (`roles`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_roles)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_roles_tenant_id)` | Multi-tenancy isolation key |
| `name` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_roles_name)` | Role name (e.g. `admin`, `operator`) |
| `description` | `TEXT` | `NULLABLE` | — | Role description |
| `is_system` | `BOOLEAN` | `NOT NULL` | `DEFAULT FALSE` | Flag indicating predefined system role |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'` | Role status (`active`, `inactive`) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. RBAC Design & Uniqueness

- **Tenant Scope**: Roles are tenant-scoped, allowing different tenants to define custom role names independently.
- **Uniqueness**: Composite unique constraint:
  ```sql
  CONSTRAINT uq_roles_tenant_id_name UNIQUE (tenant_id, name)
  ```
- **System Roles**: Predefined platform roles (`is_system = TRUE`) are protected from arbitrary tenant deletion or modification.
