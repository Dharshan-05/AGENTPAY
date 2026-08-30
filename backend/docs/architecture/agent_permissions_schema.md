# AGENTPAY Agent Permissions Schema Architecture (Phase 035)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent permission assignment table `agent_permissions` in **AGENTPAY** (`Phase 035`).

`agent_permissions` provides direct permission assignments to autonomous Agents, independent of User RBAC.

---

## 1. Table Schema Layout (`agent_permissions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_permissions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_permissions_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_permissions_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_agent_permissions_agent_id)` | Agent principal reference |
| `permission_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_permissions_permission_id_permissions) REFERENCES permissions(id) ON DELETE RESTRICT`, `INDEX (ix_agent_permissions_permission_id)` | Permission reference |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Security & Constraints

- **Composite Uniqueness**: Unique constraint `uq_agent_permissions_agent_id_permission_id` on `(agent_id, permission_id)` prevents duplicate permission assignments to the same Agent.
- **Tenant Isolation**: `agent_permissions.tenant_id == agents.tenant_id`. Every permission assignment belongs strictly to a single tenant context.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on both `agent_id` and `permission_id`.
- **RBAC Separation**: Agent permission assignments do NOT modify or share User permission tables (`user_roles`, `role_permissions`).
