# AGENTPAY Agent Audit Schema Architecture (Phase 040)

## Executive Summary

This document formalizes the architectural specification and schema layout for the immutable append-only agent audit table `agent_audit` in **AGENTPAY** (`Phase 040`).

`agent_audit` captures security-relevant events, administrative actions, lifecycle updates, credential/session modifications, and operational events for autonomous Agents.

---

## 1. Table Schema Layout (`agent_audit`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_audit)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_audit_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_audit_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_agent_audit_agent_id)` | Foreign key referencing agents |
| `actor_type` | `VARCHAR(50)` | `NOT NULL` | `INDEX (ix_agent_audit_actor_type)` | Actor category (`user`, `agent`, `system`, `service`) |
| `actor_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_audit_actor_id)` | Actor identifier |
| `event_type` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_agent_audit_event_type)` | Event classification string |
| `event_action` | `VARCHAR(100)` | `NOT NULL` | — | Specific action performed |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'` | Event outcome (`success`, `failure`, `denied`) |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | — | Traceable correlation/request ID |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | Client/service IP address |
| `user_agent` | `VARCHAR(255)` | `NULLABLE` | — | Client user-agent string |
| `event_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Extensible non-secret event JSONB context payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_agent_audit_occurred_at)` | Event occurrence timestamp (UTC) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record insertion timestamp (UTC) |

---

## 2. Immutability & Security Rules

- **Append-Only Architecture**: `agent_audit` contains NO `updated_at` and NO `deleted_at`. Updates and deletions are strictly FORBIDDEN by design.
- **Tenant Isolation**: `agent_audit.tenant_id` guarantees multi-tenant event filtering. Cross-tenant event logging is strictly REJECTED.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id`. Audit history cannot be implicitly erased by agent deletion.
- **Zero Secrets**: Authorization headers, bearer tokens, API keys, passwords, and private keys are NEVER logged into `event_metadata`.
- **Repr Safety**: `event_metadata` is explicitly excluded from `__repr__` output.
