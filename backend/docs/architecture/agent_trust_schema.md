# AGENTPAY Agent Trust Schema Architecture (Phase 039)

## Executive Summary

This document formalizes the architectural specification and schema layout for the agent security posture and trust evaluation table `agent_trust` in **AGENTPAY** (`Phase 039`).

`agent_trust` maintains the current security posture, trust status (`unknown`, `trusted`, `conditional`, `restricted`, `untrusted`), numerical trust score (`0.00`–`100.00`), and evaluation metadata for an Agent.

---

## 1. Table Schema Layout (`agent_trust`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_agent_trust)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_agent_trust_tenant_id)` | Multi-tenancy isolation key |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_agent_trust_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `UNIQUE (uq_agent_trust_agent_id)`, `INDEX (ix_agent_trust_agent_id)` | 1-to-1 foreign key referencing agents |
| `trust_status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'unknown'`, `INDEX (ix_agent_trust_trust_status)` | Trust classification status |
| `trust_score` | `NUMERIC(5,2)` | `NULLABLE` | `CHECK (trust_score IS NULL OR (trust_score >= 0 AND trust_score <= 100))` | Numerical trust rating (0.00 to 100.00) |
| `trust_reason` | `VARCHAR(255)` | `NULLABLE` | — | Non-sensitive trust evaluation reason |
| `trust_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Extensible non-sensitive posture JSONB payload |
| `evaluated_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Timestamp of last trust evaluation |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |

---

## 2. Security & Constraints

- **One-to-One Agent Relationship**: Unique constraint `uq_agent_trust_agent_id` guarantees at most one current trust record per Agent.
- **Tenant Isolation**: `agent_trust.tenant_id == agents.tenant_id`. Cross-tenant trust association is strictly REJECTED.
- **Foreign Key Delete Policy**: `ON DELETE RESTRICT` on `agent_id`.
- **Score Range Constraint**: `ck_agent_trust_score_range` ensures trust_score remains bounded between 0.00 and 100.00.
- **Zero Secrets**: Credentials, tokens, and private keys are NEVER stored in `trust_reason` or `trust_metadata`.
- **Repr Safety**: `trust_metadata` is explicitly excluded from `__repr__` output.
