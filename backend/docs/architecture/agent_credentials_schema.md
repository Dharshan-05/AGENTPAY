# AGENTPAY Agent Credentials Schema Architecture (Phase 033)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent credential verification table `agent_credentials` in **AGENTPAY** (`Phase 033`).

`agent_credentials` maintains one-way cryptographic verification hashes (`secret_hash`) and safe lookup identifiers for Agent credentials, with ZERO plaintext secrets.

---

## 1. Table Schema Layout (`agent_credentials`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_credentials)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_credentials_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_credentials_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_agent_credentials_agent_id)` | Agent ownership reference |
| `credential_type` | `VARCHAR(50)` | `NOT NULL` | — | Credential type (`api_key`, `service_secret`, etc.) |
| `credential_identifier` | `VARCHAR(255)` | `NULLABLE` | `INDEX (ix_agent_credentials_credential_identifier)` | Non-secret lookup / public key ID |
| `secret_hash` | `VARCHAR(255)` | `NOT NULL` | — | One-way verification digest (NEVER raw secret) |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_agent_credentials_status)` | Credential state (`active`, `revoked`, `expired`) |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_agent_credentials_expires_at)` | Expiration timestamp boundary |
| `revoked_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Revocation timestamp |
| `replaced_by_credential_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_agent_credentials_replaced_by_credential_id_agent_credentials) REFERENCES agent_credentials(id) ON DELETE RESTRICT` | Self-referencing rotation link |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Delete Policy

- **Zero Plaintext Secrets**: Plaintext API keys, bearer tokens, passwords, and private keys are NEVER stored in `agent_credentials`.
- **One-Way Digest**: `secret_hash` stores a non-reversible cryptographic hash used solely for verification.
- **Repr & Log Safety**: `secret_hash` is explicitly excluded from `__repr__`, exception tracebacks, and log formatters.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id` and `replaced_by_credential_id`.
