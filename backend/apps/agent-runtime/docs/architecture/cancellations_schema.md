# AGENTPAY Cancellations Schema Architecture (Phase 066)

## Executive Summary

This document formalizes the architectural specification and schema layout for `cancellations` in **AGENTPAY** (`Phase 066`).

`cancellations` represents an explicit cancellation request/action against a payment order or payment transaction prior to or during processing.

> [!IMPORTANT]
> **Domain Distinction**: `cancellations` terminates an order/payment process prior to completion. `refunds` returns money after a payment has been captured/completed. Both models are strictly segregated.

---

## 1. Schema Specifications (`cancellations`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_cancellations)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_cancellations_tenant_id)` | Multi-tenancy isolation key |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_cancellations_payment_order_id)` | FK to payment_orders |
| `payment_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_cancellations_payment_transaction_id)` | FK to payment_transactions |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_cancellations_merchant_id)` | FK to merchants |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_cancellations_agent_id)` | FK to agents |
| `cancellation_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_cancellations_tenant_id_cancellation_reference)`, `INDEX (ix_cancellations_cancellation_reference)` | Tenant-scoped cancellation reference |
| `provider_cancellation_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_cancellations_provider_cancellation_reference)` | Non-secret provider cancellation reference |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'requested'`, `CHECK (status IN ('requested', 'processing', 'completed', 'failed', 'rejected'))`, `INDEX (ix_cancellations_status)` | Cancellation status |
| `reason_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'customer_request'`, `CHECK (reason_type IN ('customer_request', 'merchant_request', 'payment_timeout', 'duplicate_order', 'system_error', 'risk_rejection', 'other'))`, `INDEX (ix_cancellations_reason_type)` | Reason classification |
| `reason_detail` | `VARCHAR(500)` | `NULLABLE` | — | Safe human-readable reason details |
| `cancellation_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata payload |
| `requested_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_cancellations_requested_at)` | Request timestamp |
| `processed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Processing timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Completion timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Failure timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_cancellations_created_at)` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |

---

## 2. Security Controls & Guidelines

- **Zero Payment Secrets**: Credit card numbers, CVV, PIN, OTP, API keys, or private authorization tokens MUST NOT be stored in `cancellation_metadata` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Provider References**: Only non-secret provider reference IDs are stored.
