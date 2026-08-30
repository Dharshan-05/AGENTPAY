# AGENTPAY Agent Sessions Schema Architecture (Phase 034)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent session context table `agent_sessions` in **AGENTPAY** (`Phase 034`).

`agent_sessions` maintains active and historical runtime session boundaries for Agents, separate from human user sessions (`sessions`).

---

## 1. Table Schema Layout (`agent_sessions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_sessions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_sessions_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_sessions_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_agent_sessions_agent_id)` | Agent ownership reference |
| `credential_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_agent_sessions_credential_id_agent_credentials) REFERENCES agent_credentials(id) ON DELETE RESTRICT`, `INDEX (ix_agent_sessions_credential_id)` | Optional credential reference |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_agent_sessions_status)` | Session state (`active`, `expired`, `revoked`) |
| `device_id` | `VARCHAR(255)` | `NULLABLE` | — | Device / runtime identifier |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | Client IP address context |
| `user_agent` | `TEXT` | `NULLABLE` | — | User-Agent string context |
| `session_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Structured non-secret session metadata payload |
| `last_activity_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp of last activity |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL` | `INDEX (ix_agent_sessions_expires_at)` | Session expiration timestamp boundary |
| `revoked_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Session revocation timestamp |
| `revocation_reason` | `VARCHAR(255)` | `NULLABLE` | — | Human-readable revocation reason |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Delete Policy

- **Tenant Isolation**: `agent_sessions.tenant_id == agents.tenant_id`. Cross-tenant agent session association is strictly REJECTED.
- **Zero Raw Bearer Tokens**: Raw session tokens are NEVER stored in `agent_sessions`.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id` and `credential_id`.
- **Metadata Security**: `session_metadata` JSONB payload MUST NOT contain tokens, private keys, or passwords.
