# AGENTPAY Reviewer Activity Schema Architecture (Phase 071)

## Executive Summary

This document formalizes the architectural specification and schema layout for `reviewer_activity` in **AGENTPAY** (`Phase 071`).

`reviewer_activity` provides an append-only, immutable activity log of reviewer actions within review and approval workflows.

---

## 1. Schema Specifications (`reviewer_activity`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_reviewer_activity)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_reviewer_activity_tenant_id)` | Multi-tenancy isolation key |
| `reviewer_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_reviewer_activity_reviewer_id)` | Reviewer user UUID (FK to users) |
| `review_queue_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_reviewer_activity_review_queue_id)` | Optional FK to review_queue |
| `approval_request_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_reviewer_activity_approval_request_id)` | Optional FK to approval_requests |
| `approval_decision_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_reviewer_activity_approval_decision_id)` | Optional FK to approval_decisions |
| `activity_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_reviewer_activity_tenant_id_activity_reference)`, `INDEX (ix_reviewer_activity_activity_reference)` | Tenant-scoped activity reference |
| `activity_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'review'`, `CHECK (activity_type IN ('review', 'approval', 'decision', 'comment', 'assignment', 'escalation', 'claim'))`, `INDEX (ix_reviewer_activity_activity_type)` | Activity classification |
| `activity_action` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'viewed'`, `CHECK (activity_action IN ('assigned', 'viewed', 'opened', 'claimed', 'commented', 'approved', 'rejected', 'escalated', 'reassigned', 'requested_information', 'released', 'skipped', 'expired'))`, `INDEX (ix_reviewer_activity_activity_action)` | Specific reviewer action |
| `actor_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'user'` | Actor type classification |
| `actor_id` | `UUID` | `NULLABLE` | `INDEX (ix_reviewer_activity_actor_id)` | Actor UUID |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_reviewer_activity_request_id)` | Correlation request ID |
| `activity_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_reviewer_activity_occurred_at)` | Activity occurrence timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Security Controls & Guidelines

- **Append-Only Immutability**: No `updated_at` or `deleted_at` columns exist. Records are append-only.
- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `activity_payload` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
