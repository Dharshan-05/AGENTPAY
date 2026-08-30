# AGENTPAY Agents Schema Architecture (Phase 031)

## Executive Summary

This document formalizes the architectural specification and schema layout for the platform-level agent principal table `agents` in **AGENTPAY** (`Phase 031`).

Agents in AGENTPAY are first-class autonomous principals (separate from human user identity) owned by a tenant (`tenant_id`).

---

## 1. Table Schema Layout (`agents`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agents)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agents_tenant_id)` | Multi-tenancy isolation key |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Human-readable agent principal name |
| `slug` | `VARCHAR(255)` | `NOT NULL` | `UNIQUE (uq_agents_tenant_id_slug: tenant_id, slug)`, `INDEX (ix_agents_slug)` | Tenant-scoped agent slug identifier |
| `agent_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'autonomous'` | Agent class (`autonomous`, `service`, `workflow`, etc.) |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `INDEX (ix_agents_status)` | Agent status (`active`, `inactive`, `suspended`) |
| `description` | `TEXT` | `NULLABLE` | — | Operational description |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Security & Domain Boundary Rules

- **First-Class Principal**: Agents maintain their own identity boundary. `agents.id` is NOT derived from `users.id`.
- **Tenant Isolation**: `tenant_id UUID NOT NULL` guarantees that every agent belongs to a tenant context. `uq_agents_tenant_id_slug` prevents slug collisions within the same tenant.
- **Zero Credentials**: Credentials, API keys, bearer tokens, or secrets are NEVER stored in `agents`.
