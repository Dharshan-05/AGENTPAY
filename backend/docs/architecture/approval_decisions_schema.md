# AGENTPAY Approval Decisions Schema Architecture (Phase 070)

## Executive Summary

This document formalizes the architectural specification and schema layout for `approval_decisions` in **AGENTPAY** (`Phase 070`).

`approval_decisions` records individual reviewer decision actions taken against approval requests.

---

## 1. Schema Specifications (`approval_decisions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_approval_decisions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_approval_decisions_tenant_id)` | Multi-tenancy isolation key |
| `approval_request_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_decisions_approval_request_id)` | Parent approval request UUID |
| `reviewer_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_decisions_reviewer_id)` | Reviewer user UUID (FK to users) |
| `decision_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_approval_decisions_tenant_id_decision_reference)`, `INDEX (ix_approval_decisions_decision_reference)` | Tenant-scoped decision reference |
| `decision` | `VARCHAR(50)` | `NOT NULL` | `CHECK (decision IN ('approved', 'rejected', 'abstained', 'cancelled'))`, `INDEX (ix_approval_decisions_decision)` | Decision action classification |
| `reason` | `VARCHAR(500)` | `NULLABLE` | — | Decision rationale summary |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_approval_decisions_request_id)` | Correlation request ID |
| `decision_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret decision metadata payload |
| `decided_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_approval_decisions_decided_at)` | Decision timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |

---

## 2. Security Controls & Guidelines

- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `decision_context` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Foreign Keys**: `approval_request_id` -> `approval_requests.id` (`ON DELETE RESTRICT`) and `reviewer_id` -> `users.id` (`ON DELETE RESTRICT`).
