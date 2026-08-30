# AGENTPAY Refunds Schema Architecture (Phase 065)

## Executive Summary

This document formalizes the architectural specification and schema layout for `refunds` in **AGENTPAY** (`Phase 065`).

`refunds` represents the financial reversal of a completed or captured payment transaction.

> [!IMPORTANT]
> **Domain Distinction**: `cancellations` terminates an order/payment process prior to completion. `refunds` returns money after a payment has been captured/completed.

---

## 1. Schema Specifications (`refunds`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_refunds)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_refunds_tenant_id)` | Multi-tenancy isolation key |
| `payment_transaction_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_refunds_payment_transaction_id)` | FK to payment_transactions |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_refunds_payment_order_id)` | FK to payment_orders |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_refunds_commerce_transaction_id)` | FK to commerce_transactions |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_refunds_merchant_id)` | FK to merchants |
| `refund_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_refunds_tenant_id_refund_reference)`, `INDEX (ix_refunds_refund_reference)` | Tenant-scoped refund reference |
| `external_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_refunds_external_reference)` | External reference |
| `provider_refund_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_refunds_provider_refund_reference)` | Non-secret provider refund ID |
| `refund_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'full'`, `CHECK (refund_type IN ('full', 'partial'))`, `INDEX (ix_refunds_refund_type)` | Refund classification |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))`, `INDEX (ix_refunds_status)` | Refund status |
| `amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (amount > 0)` | Refund monetary amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | Currency code |
| `reason` | `VARCHAR(500)` | `NULLABLE` | — | Human-readable refund reason |
| `refund_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata payload |
| `requested_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_refunds_requested_at)` | Request timestamp |
| `processed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Processing timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Completion timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Failure timestamp |
| `cancelled_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Cancellation timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_refunds_created_at)` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Financial Precision & Security

- **Decimal Semantics**: `amount` MUST be Decimal `NUMERIC(18,4)`. `FLOAT` and `REAL` are strictly prohibited.
- **Positive Amount**: `amount > 0` is strictly enforced.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Zero Payment Secrets**: Credit card numbers, CVV, PIN, OTP, API keys, or private authorization tokens MUST NOT be stored in `refund_metadata` or exposed in `__repr__`.
