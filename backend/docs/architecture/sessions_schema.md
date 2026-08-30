# AGENTPAY Sessions Schema Architecture (Phase 027)

## Executive Summary

This document formalizes the architectural specification and schema layout for the authentication session table `sessions` in **AGENTPAY** (`Phase 027`).

The `sessions` schema tracks active, revoked, and expired user/device authentication contexts with multi-tenant isolation (`tenant_id`).

---

## 1. Table Schema Layout (`sessions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_sessions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_sessions_tenant_id)` | Multi-tenancy isolation key |
| `user_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_sessions_user_id_users) REFERENCES users(id) ON DELETE RESTRICT`, `INDEX (ix_sessions_user_id)` | Foreign key referencing users |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_sessions_status)` | Lifecycle status (`active`, `revoked`, `expired`) |
| `device_id` | `VARCHAR(255)` | `NULLABLE` | — | Non-sensitive device context identifier |
| `user_agent` | `TEXT` | `NULLABLE` | — | Client user-agent string |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | Client IP address context |
| `last_activity_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Last authenticated activity timestamp |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL` | `INDEX (ix_sessions_expires_at)` | Session expiration boundary timestamp |
| `revoked_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Explicit session revocation timestamp |
| `revocation_reason` | `VARCHAR(255)` | `NULLABLE` | — | Reason for explicit session revocation |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Delete Policy

- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `fk_sessions_user_id_users` prevents accidental user deletion while active authentication session history exists.
- **Zero Raw Tokens**: Plaintext session tokens or bearer secrets are NEVER stored in `sessions`.
