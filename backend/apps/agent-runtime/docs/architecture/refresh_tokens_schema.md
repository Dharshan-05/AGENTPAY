# AGENTPAY Refresh Tokens Schema Architecture (Phase 028)

## Executive Summary

This document formalizes the architectural specification and schema layout for the cryptographic refresh token registry table `refresh_tokens` in **AGENTPAY** (`Phase 028`).

The `refresh_tokens` schema provides rotation readiness, token family tracking, revocation capability, and reuse-detection readiness.

---

## 1. Table Schema Layout (`refresh_tokens`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_refresh_tokens)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_refresh_tokens_tenant_id)` | Multi-tenancy isolation key |
| `session_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_refresh_tokens_session_id_sessions) REFERENCES sessions(id) ON DELETE RESTRICT`, `INDEX (ix_refresh_tokens_session_id)` | Foreign key referencing parent session |
| `token_hash` | `VARCHAR(255)` | `NOT NULL` | `UNIQUE (uq_refresh_tokens_token_hash)`, `INDEX (ix_refresh_tokens_token_hash)` | Cryptographic digest of refresh token |
| `family_id` | `UUID` | `NULLABLE` | `INDEX (ix_refresh_tokens_family_id)` | Token rotation family identifier |
| `parent_token_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_refresh_tokens_parent_token_id_refresh_tokens) REFERENCES refresh_tokens(id) ON DELETE RESTRICT` | Parent refresh token reference in rotation chain |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_refresh_tokens_status)` | Lifecycle status (`active`, `rotated`, `revoked`, `expired`) |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL` | `INDEX (ix_refresh_tokens_expires_at)` | Token expiration boundary timestamp |
| `rotated_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp when token was rotated |
| `revoked_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp when token was revoked |
| `reuse_detected_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp when token reuse attempt was detected |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. High-Risk Security Rules

- **Zero Plaintext Tokens**: Raw refresh tokens are NEVER persisted. Only deterministic cryptographic hashes (`token_hash`) are stored.
- **Representation Protection**: `token_hash` is excluded from string representations (`__repr__`) and log outputs.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `session_id` and `parent_token_id`.
