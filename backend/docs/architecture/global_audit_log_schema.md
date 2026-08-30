# AGENTPAY Global Audit Log Schema Architecture (Phase 072)

## Executive Summary

This document formalizes the architectural specification and schema layout for `audit_logs` in **AGENTPAY** (`Phase 072`).

`audit_logs` provides the central, multi-tenant, platform-wide immutable audit trail for security, identity, authorization, commerce, payment, policy, review, and system operations.

---

## 1. Schema Specifications (`audit_logs`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_audit_logs)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_audit_logs_tenant_id)` | Multi-tenancy isolation key |
| `audit_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_audit_logs_tenant_id_audit_reference)`, `INDEX (ix_audit_logs_audit_reference)` | Tenant-scoped audit reference |
| `actor_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'user'`, `INDEX (ix_audit_logs_actor_type)` | Actor classification |
| `actor_id` | `UUID` | `NULLABLE` | `INDEX (ix_audit_logs_actor_id)` | Generic actor UUID |
| `user_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_audit_logs_user_id)` | User actor UUID |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_audit_logs_agent_id)` | Agent actor UUID |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_audit_logs_merchant_id)` | Merchant actor UUID |
| `resource_type` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_audit_logs_resource_type)` | Target resource entity type |
| `resource_id` | `UUID` | `NULLABLE` | `INDEX (ix_audit_logs_resource_id)` | Target resource UUID |
| `action` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_audit_logs_action)` | Specific audited action |
| `category` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'system'`, `CHECK (category IN ('authentication', 'authorization', 'security', 'policy', 'commerce', 'payment', 'approval', 'review', 'configuration', 'agent', 'merchant', 'system'))`, `INDEX (ix_audit_logs_category)` | Audit category |
| `result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'`, `CHECK (result IN ('success', 'failure', 'denied', 'error'))`, `INDEX (ix_audit_logs_result)` | Outcome result |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_audit_logs_request_id)` | Correlation request ID |
| `correlation_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_audit_logs_correlation_id)` | Cross-service correlation ID |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | Network IP context |
| `user_agent` | `VARCHAR(500)` | `NULLABLE` | — | HTTP user agent context |
| `before_state` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret pre-action state snapshot |
| `after_state` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret post-action state snapshot |
| `metadata_json` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret audit metadata |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_audit_logs_occurred_at)` | Occurrence timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Security Controls & Guidelines

- **Append-Only Immutability**: No `updated_at` or `deleted_at` columns exist. Audit logs are strictly immutable.
- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `before_state`, `after_state`, `metadata_json`, or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
