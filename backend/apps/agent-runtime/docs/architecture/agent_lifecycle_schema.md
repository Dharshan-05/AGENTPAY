# AGENTPAY Agent Lifecycle Schema Architecture (Phase 037)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent operational lifecycle table `agent_lifecycle` in **AGENTPAY** (`Phase 037`).

`agent_lifecycle` maintains the current runtime operational state of an Agent (`provisioning`, `active`, `paused`, `suspended`, `deactivated`) with state transition timestamps and reason codes.

---

## 1. Table Schema Layout (`agent_lifecycle`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_lifecycle)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_lifecycle_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_lifecycle_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `UNIQUE (uq_agent_lifecycle_agent_id)`, `INDEX (ix_agent_lifecycle_agent_id)` | 1-to-1 foreign key referencing agents |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'provisioning'`, `INDEX (ix_agent_lifecycle_status)` | Operational state (`provisioning`, `active`, `paused`, `suspended`, `deactivated`) |
| `status_reason` | `VARCHAR(255)` | `NULLABLE` | — | Non-sensitive operational reason string |
| `activated_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Activation timestamp |
| `paused_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Pause timestamp |
| `suspended_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Suspension timestamp |
| `deactivated_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Deactivation timestamp |
| `last_transition_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp of most recent state change |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Constraints

- **One-to-One Agent Relationship**: Unique constraint `uq_agent_lifecycle_agent_id` guarantees exactly one current lifecycle state record per Agent.
- **Tenant Isolation**: `agent_lifecycle.tenant_id == agents.tenant_id`. Every lifecycle record belongs to a single tenant.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id`.
- **Zero Secrets**: Plaintext secrets, tokens, or credentials are NEVER stored in `status_reason`.
