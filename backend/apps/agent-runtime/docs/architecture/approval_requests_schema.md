# AGENTPAY Approval Requests Schema Architecture (Phase 069)

## Executive Summary

This document formalizes the architectural specification and schema layout for `approval_requests` in **AGENTPAY** (`Phase 069`).

`approval_requests` represents explicit multi-approval authorization requests requiring decision makers.

---

## 1. Schema Specifications (`approval_requests`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_approval_requests)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_approval_requests_tenant_id)` | Multi-tenancy isolation key |
| `approval_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_approval_requests_tenant_id_approval_reference)`, `INDEX (ix_approval_requests_approval_reference)` | Tenant-scoped approval reference |
| `approval_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'payment'`, `CHECK (approval_type IN ('payment', 'transaction', 'refund', 'cancellation', 'security', 'risk', 'fraud', 'commerce', 'agent', 'policy', 'manual'))`, `INDEX (ix_approval_requests_approval_type)` | Approval classification |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'in_review', 'partially_approved', 'approved', 'rejected', 'expired', 'cancelled'))`, `INDEX (ix_approval_requests_status)` | Approval lifecycle status |
| `priority` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (priority >= 0)`, `INDEX (ix_approval_requests_priority)` | Priority rank |
| `requested_action` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'authorize'`, `CHECK (requested_action IN ('authorize', 'capture', 'refund', 'cancel', 'execute', 'allow', 'deny', 'override', 'escalate'))` | Requested action |
| `requested_amount` | `NUMERIC(18,4)` | `NULLABLE` | `CHECK (requested_amount IS NULL OR requested_amount >= 0)` | Requested monetary amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | Currency code |
| `requester_type` | `VARCHAR(100)` | `NULLABLE` | — | Requester type |
| `requester_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_requests_requester_id)` | FK to users |
| `target_reviewer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_requests_target_reviewer_id)` | FK to users |
| `required_approvals` | `INTEGER` | `NOT NULL` | `DEFAULT 1`, `CHECK (required_approvals > 0)` | Required approval count threshold |
| `received_approvals` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (received_approvals >= 0)`, `CHECK (received_approvals <= required_approvals)` | Accumulated approval counter |
| `source_type` | `VARCHAR(100)` | `NULLABLE` | — | Generic source entity type |
| `source_id` | `UUID` | `NULLABLE` | `INDEX (ix_approval_requests_source_id)` | Generic source UUID |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to policy_rules |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to policy_evaluations |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to security_violations |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to risk_signals |
| `fraud_prediction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to fraud_predictions |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to commerce_transactions |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_requests_payment_order_id)` | FK to payment_orders |
| `payment_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_approval_requests_payment_transaction_id)` | FK to payment_transactions |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT` | FK to merchants |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_approval_requests_request_id)` | Correlation request ID |
| `reason` | `VARCHAR(500)` | `NULLABLE` | — | Human-readable approval reason |
| `approval_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret approval metadata payload |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_approval_requests_expires_at)` | Request expiration timestamp |
| `requested_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_approval_requests_requested_at)` | Request creation timestamp |
| `started_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Review start timestamp |
| `resolved_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Resolution timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Security Controls & Guidelines

- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `approval_context` or exposed in `__repr__`.
- **Financial Precision**: `requested_amount` MUST be Decimal `NUMERIC(18,4)`. `FLOAT` and `REAL` are strictly prohibited.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Identity Relationships**: `requester_id` and `target_reviewer_id` explicitly link to `users.id` (`ON DELETE RESTRICT`).
