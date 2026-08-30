# AGENTPAY Login & Security Events Schema Architecture (Phase 030)

## Executive Summary

This document formalizes the architectural specification and schema layout for the immutable security event log table `login_security_events` in **AGENTPAY** (`Phase 030`).

The `login_security_events` schema provides an append-only historical audit trail for authentication successes, failures, logouts, session revocations, and security alerts.

---

## 1. Table Schema Layout (`login_security_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_login_security_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_login_security_events_tenant_id)` | Multi-tenancy isolation key |
| `user_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_login_security_events_user_id_users) REFERENCES users(id) ON DELETE RESTRICT`, `INDEX (ix_login_security_events_user_id)` | Nullable user ID for pre-auth/failed attempts |
| `session_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_login_security_events_session_id_sessions) REFERENCES sessions(id) ON DELETE RESTRICT`, `INDEX (ix_login_security_events_session_id)` | Nullable session reference |
| `refresh_token_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_login_security_events_refresh_token_id_refresh_tokens) REFERENCES refresh_tokens(id) ON DELETE RESTRICT`, `INDEX (ix_login_security_events_refresh_token_id)` | Nullable refresh token reference |
| `event_type` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_login_security_events_event_type)` | Event classification (`login_success`, `login_failure`, `logout`, etc.) |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'` | Result outcome (`success`, `failure`) |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | Client IP address context |
| `user_agent` | `TEXT` | `NULLABLE` | — | Client user-agent string |
| `request_id` | `VARCHAR(255)` | `NULLABLE` | — | Request correlation tracking ID |
| `event_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Structured event context metadata (ZERO secrets) |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_login_security_events_occurred_at)` | Authoritative event occurrence timestamp |

---

## 2. Immutability & Security Audit Rules

- **Append-Only Immutability**: `login_security_events` contains NO `updated_at` or `deleted_at` columns. Application repositories expose append-only creation behavior without mutation or soft-deletion.
- **Zero Secrets in JSONB**: `event_metadata` is strictly prohibited from containing raw tokens, passwords, bearer tokens, or private keys.
- **Nullable Context References**: `user_id`, `session_id`, and `refresh_token_id` are nullable to allow logging pre-authentication security events and attempts from unauthenticated clients.
