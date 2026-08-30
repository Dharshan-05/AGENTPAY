# AGENTPAY Role-Permission Schema Architecture (Phase 025)

## Executive Summary

This document formalizes the architectural specification and schema layout for the role-permission junction table `role_permissions` in **AGENTPAY** (`Phase 025`).

The `role_permissions` schema connects tenant-scoped roles (`roles`) to global platform capabilities (`permissions`), enforcing normalized RBAC relationships without relying on JSONB arrays.

---

## 1. Table Schema Layout (`role_permissions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_role_permissions)` | Canonical primary key (UUIDv7) |
| `role_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_role_permissions_role_id_roles) REFERENCES roles(id) ON DELETE RESTRICT`, `INDEX (ix_role_permissions_role_id)` | Foreign key referencing roles |
| `permission_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_role_permissions_permission_id_permissions) REFERENCES permissions(id) ON DELETE RESTRICT`, `INDEX (ix_role_permissions_permission_id)` | Foreign key referencing permissions |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Uniqueness & Foreign Key Delete Policy

- **Duplicate Assignment Prevention**: Enforced via composite unique constraint:
  ```sql
  CONSTRAINT uq_role_permissions_role_id_permission_id UNIQUE (role_id, permission_id)
  ```
- **Foreign Key Delete Policy**: Both `role_id` and `permission_id` foreign keys enforce `ON DELETE RESTRICT` to prevent silent cascading removal of permission assignments.
- **Tenant Integrity**: Derived via `role_id -> roles.tenant_id` where `roles` is tenant-isolated and `permissions` represents global capabilities.
