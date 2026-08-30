# AGENTPAY Permissions Schema Architecture (Phase 024)

## Executive Summary

This document formalizes the architectural specification and schema layout for atomic permission capabilities table `permissions` in **AGENTPAY** (`Phase 024`).

Permissions represent global, immutable platform capabilities that map fine-grained resource and action domains.

---

## 1. Table Schema Layout (`permissions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_permissions)` | Canonical primary key (UUIDv7) |
| `name` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_permissions_name)`, `INDEX (ix_permissions_name)` | Canonical permission string (e.g. `users.read`) |
| `resource` | `VARCHAR(50)` | `NOT NULL` | `INDEX (ix_permissions_resource)` | Target domain resource (e.g. `users`, `agents`) |
| `action` | `VARCHAR(50)` | `NOT NULL` | — | Target action capability (e.g. `read`, `execute`) |
| `description` | `TEXT` | `NULLABLE` | — | Permission description |
| `is_system` | `BOOLEAN` | `NOT NULL` | `DEFAULT TRUE` | Platform system permission flag |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. RBAC Design & Uniqueness

- **Global Capability Scope**: Permissions are global system definitions shared across all tenants.
- **Uniqueness**: Enforced via unique constraint on `name`:
  ```sql
  CONSTRAINT uq_permissions_name UNIQUE (name)
  ```
- **Normalization**: Core permission relationships (`role_permissions`) will be normalized via dedicated junction tables in subsequent phases (Phase 025). No JSONB array columns are used.
