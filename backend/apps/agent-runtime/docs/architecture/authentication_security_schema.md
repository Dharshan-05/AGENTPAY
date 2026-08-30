# AGENTPAY Authentication Security Schema Architecture (Phase 029)

## Executive Summary

This document formalizes the architectural specification and schema layout for the user authentication security state table `authentication_security` in **AGENTPAY** (`Phase 029`).

The `authentication_security` schema tracks login failure counters, account lockout timestamps, password security metadata, and account status with multi-tenant isolation (`tenant_id`).

---

## 1. Table Schema Layout (`authentication_security`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_authentication_security)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_authentication_security_tenant_id)` | Multi-tenancy isolation key |
| `user_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_authentication_security_user_id_users) REFERENCES users(id) ON DELETE RESTRICT`, `UNIQUE (uq_authentication_security_user_id)`, `INDEX (ix_authentication_security_user_id)` | 1-to-1 foreign key referencing users |
| `failed_login_attempts` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (ck_authentication_security_failed_login_attempts_nonnegative: >= 0)` | Consecutive failed login counter |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_authentication_security_status)` | Security status (`active`, `locked`, `disabled`) |
| `locked_until` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_authentication_security_locked_until)` | Temporary lockout expiry boundary |
| `locked_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp when account was locked |
| `disabled_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp when account was disabled |
| `password_changed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Password change metadata timestamp |
| `password_expires_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Password expiration boundary timestamp |
| `last_successful_login_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Last successful authentication timestamp |
| `last_failed_login_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Last failed authentication timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Delete Policy

- **One-to-One User Relationship**: Unique constraint `uq_authentication_security_user_id` guarantees at most one current security state record per user.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `fk_authentication_security_user_id_users` prevents deletion of user records with active security state.
- **Zero Credentials**: Plaintext passwords, password hashes, or reset tokens are NEVER stored in `authentication_security`.
