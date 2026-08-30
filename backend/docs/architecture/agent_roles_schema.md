# AGENTPAY Agent Roles Schema Architecture (Phase 036)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent role assignment table `agent_roles` in **AGENTPAY** (`Phase 036`).

`agent_roles` provides role assignments to autonomous Agents, independent of User RBAC.

---

## 1. Table Schema Layout (`agent_roles`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_roles)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_roles_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_roles_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_agent_roles_agent_id)` | Agent principal reference |
| `role_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_roles_role_id_roles) REFERENCES roles(id) ON DELETE RESTRICT`, `INDEX (ix_agent_roles_role_id)` | Role reference |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Security & Constraints

- **Composite Uniqueness**: Unique constraint `uq_agent_roles_agent_id_role_id` on `(agent_id, role_id)` prevents duplicate role assignments to the same Agent.
- **Tenant Isolation**: `agent_roles.tenant_id == agents.tenant_id`. Every role assignment belongs strictly to a single tenant context.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on both `agent_id` and `role_id`.
- **RBAC Separation**: Agent role assignments do NOT modify or share User role tables (`user_roles`).
