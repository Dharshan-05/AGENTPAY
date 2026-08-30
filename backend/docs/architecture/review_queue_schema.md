# AGENTPAY Review Queue Schema Architecture (Phase 068)

## Executive Summary

This document formalizes the architectural specification and schema layout for `review_queue` in **AGENTPAY** (`Phase 068`).

`review_queue` represents transaction, security, risk, and payment processing cases requiring human or automated review.

---

## 1. Schema Specifications (`review_queue`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_review_queue)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_review_queue_tenant_id)` | Multi-tenancy isolation key |
| `review_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_review_queue_tenant_id_review_reference)`, `INDEX (ix_review_queue_review_reference)` | Tenant-scoped review reference |
| `review_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'security'`, `CHECK (review_type IN ('security', 'risk', 'fraud', 'payment', 'transaction', 'authorization', 'compliance', 'manual', 'agent', 'commerce'))`, `INDEX (ix_review_queue_review_type)` | Review classification |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'queued'`, `CHECK (status IN ('queued', 'assigned', 'in_review', 'approved', 'rejected', 'escalated', 'resolved', 'cancelled'))`, `INDEX (ix_review_queue_status)` | Review status |
| `priority` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (priority >= 0)`, `INDEX (ix_review_queue_priority)` | Priority rank |
| `severity` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'medium'`, `CHECK (severity IN ('low', 'medium', 'high', 'critical'))`, `INDEX (ix_review_queue_severity)` | Severity level |
| `source_type` | `VARCHAR(100)` | `NULLABLE` | — | Generic source entity type |
| `source_id` | `UUID` | `NULLABLE` | `INDEX (ix_review_queue_source_id)` | Generic source UUID |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to policy_rules |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to policy_evaluations |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to security_violations |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to risk_signals |
| `fraud_prediction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to fraud_predictions |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to commerce_transactions |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_review_queue_payment_order_id)` | FK to payment_orders |
| `payment_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_review_queue_payment_transaction_id)` | FK to payment_transactions |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to merchants |
| `assigned_reviewer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_review_queue_assigned_reviewer_id)` | FK to users (Reviewer identity) |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_review_queue_request_id)` | Correlation request ID |
| `title` | `VARCHAR(200)` | `NOT NULL` | — | Review title |
| `description` | `VARCHAR(1000)` | `NULLABLE` | — | Review description |
| `review_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret review metadata payload |
| `decision` | `VARCHAR(50)` | `NULLABLE` | `CHECK (decision IS NULL OR decision IN ('allow', 'deny', 'approve', 'reject', 'escalate', 'cancel', 'review'))` | Review outcome decision |
| `decision_reason` | `VARCHAR(500)` | `NULLABLE` | — | Human/system reason for decision |
| `queued_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_review_queue_queued_at)` | Queue entry timestamp |
| `assigned_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Assignment timestamp |
| `started_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Review start timestamp |
| `resolved_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Resolution timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Security Controls & Guidelines

- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `review_context` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Reviewer Identity**: `assigned_reviewer_id` explicitly links to `users.id` (`ON DELETE RESTRICT`).
