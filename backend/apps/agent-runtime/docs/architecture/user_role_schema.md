# AGENTPAY User-Role Schema Architecture (Phase 026)

## Executive Summary

This document formalizes the architectural specification and schema layout for the user-role junction table `user_roles` in **AGENTPAY** (`Phase 026`).

The `user_roles` schema connects users (`users`) to assigned roles (`roles`), enforcing strict tenant isolation (`tenant_id`) and preventing cross-tenant role assignments.

---

## 1. Table Schema Layout (`user_roles`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_user_roles)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_user_roles_tenant_id)` | Multi-tenancy isolation key |
| `user_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_user_roles_user_id_users) REFERENCES users(id) ON DELETE RESTRICT`, `INDEX (ix_user_roles_user_id)` | Foreign key referencing users |
| `role_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_user_roles_role_id_roles) REFERENCES roles(id) ON DELETE RESTRICT`, `INDEX (ix_user_roles_role_id)` | Foreign key referencing roles |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Tenant Isolation & Duplicate Prevention

- **Tenant Isolation**: `tenant_id UUID NOT NULL` guarantees that `user_roles.tenant_id == users.tenant_id == roles.tenant_id`. Cross-tenant role assignment (`Tenant A user + Tenant B role`) is strictly forbidden and rejected.
- **Duplicate Role Assignment Prevention**: Enforced via composite unique constraint:
  ```sql
  CONSTRAINT uq_user_roles_user_id_role_id UNIQUE (user_id, role_id)
  ```
- **Foreign Key Delete Policy**: Both `user_id` and `role_id` foreign keys enforce `ON DELETE RESTRICT`.
