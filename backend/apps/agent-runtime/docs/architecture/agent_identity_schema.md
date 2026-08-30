# AGENTPAY Agent Identity Schema Architecture (Phase 032)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent identity profile table `agent_identities` in **AGENTPAY** (`Phase 032`).

The `agent_identities` schema provides a 1-to-1 non-credential identity profile for an `Agent`.

---

## 1. Table Schema Layout (`agent_identities`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_identities)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_identities_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_identities_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `UNIQUE (uq_agent_identities_agent_id)`, `INDEX (ix_agent_identities_agent_id)` | 1-to-1 foreign key referencing agents |
| `display_name` | `VARCHAR(255)` | `NULLABLE` | — | Display presentation name |
| `identity_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'standard'` | Identity classification (`standard`, `system`, `external`) |
| `external_reference` | `VARCHAR(255)` | `NULLABLE` | — | Non-secret external system identifier |
| `description` | `TEXT` | `NULLABLE` | — | Identity profile description |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Security & Delete Policy

- **One-to-One Agent Relationship**: Unique constraint `uq_agent_identities_agent_id` guarantees at most one current identity profile per agent.
- **Tenant Isolation**: `agent_identities.tenant_id == agents.tenant_id`. Cross-tenant agent identity creation is strictly REJECTED.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `fk_agent_identities_agent_id_agents`.
- **Zero Credentials**: Plaintext credentials, API keys, private keys, or bearer tokens are NEVER stored in `agent_identities`.
