# AGENTPAY Identity Users Schema Architecture (Phase 021)

## Executive Summary

This document formalizes the architectural specification and schema layout for the core identity entity table `users` in **AGENTPAY** (`Phase 021`).

The `users` schema provides identity foundation, multi-tenant isolation (`tenant_id`), authentication state readiness, security tracking, and audit/soft-deletion lifecycle management.

---

## 1. Table Schema Layout (`users`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_users)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_users_tenant_id)` | Multi-tenancy isolation key |
| `email` | `VARCHAR(255)` | `NOT NULL` | `INDEX (ix_users_email)` | Normalized user email address |
| `password_hash` | `VARCHAR(255)` | `NULLABLE` | — | Protected password hash (never plaintext) |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'` | Lifecycle status (`active`, `inactive`, `suspended`, `locked`, `pending`) |
| `failed_login_attempts` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (ck_users_failed_login_attempts_nonnegative)` | Consecutive failed authentication tracking |
| `locked_until` | `TIMESTAMPTZ` | `NULLABLE` | — | Lockout expiration timestamp |
| `email_verified_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Email verification timestamp |
| `last_login_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Last successful authentication timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Uniqueness & Indexing Rules

- **Tenant-Scoped Email Uniqueness**: Enforced via composite unique constraint:
  ```sql
  CONSTRAINT uq_users_tenant_id_email UNIQUE (tenant_id, email)
  ```
- **Indexes**:
  - `ix_users_tenant_id` on `(tenant_id)` for tenant isolation filtering.
  - `ix_users_email` on `(email)` for high-frequency lookup.

---

## 3. Security & Secret Protection

- Plaintext passwords, authentication tokens, and secrets are NEVER stored or logged.
- `password_hash` is marked nullable to support non-password / OAuth authentication providers, and is excluded from generic API responses and string representation (`__repr__`).
