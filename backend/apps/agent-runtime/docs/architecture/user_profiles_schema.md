# AGENTPAY User Profiles Schema Architecture (Phase 022)

## Executive Summary

This document formalizes the architectural specification and schema layout for the non-authentication user profile table `user_profiles` in **AGENTPAY** (`Phase 022`).

The `user_profiles` schema isolates personal user profile metadata from core identity and authentication state (`users`), enforcing strict one-to-one cardinality per user.

---

## 1. Table Schema Layout (`user_profiles`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_user_profiles)` | Canonical primary key (UUIDv7) |
| `user_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_user_profiles_user_id_users) REFERENCES users(id) ON DELETE RESTRICT`, `UNIQUE (uq_user_profiles_user_id)` | Parent user reference |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_user_profiles_tenant_id)` | Multi-tenancy isolation key |
| `first_name` | `VARCHAR(100)` | `NULLABLE` | — | User given name |
| `last_name` | `VARCHAR(100)` | `NULLABLE` | — | User surname / family name |
| `display_name` | `VARCHAR(150)` | `NULLABLE` | — | Public / UI display name |
| `avatar_url` | `VARCHAR(500)` | `NULLABLE` | — | Profile image reference URL |
| `phone_number` | `VARCHAR(50)` | `NULLABLE` | — | Normalized contact phone number |
| `timezone` | `VARCHAR(50)` | `NULLABLE` | — | IANA timezone identifier (e.g. `Asia/Kolkata`) |
| `locale` | `VARCHAR(20)` | `NULLABLE` | — | Regional locale tag (e.g. `en_US`) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Cardinality & Foreign Key Rules

- **One-to-One Cardinality**: Enforced at the database level via unique constraint:
  ```sql
  CONSTRAINT uq_user_profiles_user_id UNIQUE (user_id)
  ```
- **Foreign Key Delete Policy**: Enforces `ON DELETE RESTRICT` on `fk_user_profiles_user_id_users` to prevent accidental cascading deletion of parent identity records without audit traces.
- **Indexes**:
  - `ix_user_profiles_user_id` on `(user_id)`.
  - `ix_user_profiles_tenant_id` on `(tenant_id)` for tenant isolation queries.
