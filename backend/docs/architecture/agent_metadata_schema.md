# AGENTPAY Agent Metadata Schema Architecture (Phase 038)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent metadata table `agent_metadata` in **AGENTPAY** (`Phase 038`).

`agent_metadata` maintains non-security-sensitive, extensible configuration metadata for Agents using a controlled JSONB payload (`metadata_payload`).

---

## 1. Table Schema Layout (`agent_metadata`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_metadata)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_metadata_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_metadata_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `UNIQUE (uq_agent_metadata_agent_id)`, `INDEX (ix_agent_metadata_agent_id)` | 1-to-1 foreign key referencing agents |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Extensible non-sensitive metadata JSONB payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Constraints

- **One-to-One Agent Relationship**: Unique constraint `uq_agent_metadata_agent_id` guarantees at most one metadata record per Agent.
- **Tenant Isolation**: `agent_metadata.tenant_id == agents.tenant_id`. Cross-tenant metadata association is strictly REJECTED.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id`.
- **Zero Secrets**: Plaintext passwords, API keys, bearer tokens, private keys, or secrets are NEVER stored in `metadata_payload`.
- **Repr Safety**: `metadata_payload` is explicitly excluded from `__repr__` and log formatters to avoid accidental log dumping.
