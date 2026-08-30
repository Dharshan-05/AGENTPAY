# AGENTPAY Payment Transactions Schema Architecture (Phase 062)

## Executive Summary

This document formalizes the architectural specification and schema layout for `payment_transactions` in **AGENTPAY** (`Phase 062`).

`payment_transactions` represents individual payment processing attempts and financial transactions associated with a `PaymentOrder`.

> [!IMPORTANT]
> **Domain Distinction**: `commerce_transactions` represents the high-level commerce domain order/checkout transaction layer. `payment_transactions` represents the lower-level gateway/payment-processing attempt layer. Both tables exist independently with clean foreign key linkage (`payment_transactions.commerce_transaction_id`).

---

## 1. Schema Specifications (`payment_transactions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_payment_transactions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_payment_transactions_tenant_id)` | Multi-tenancy isolation key |
| `payment_order_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_transactions_payment_order_id)` | FK to payment_orders |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_transactions_merchant_id)` | FK to merchants |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_transactions_agent_id)` | FK to agents |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_transactions_commerce_transaction_id)` | FK to commerce_transactions |
| `transaction_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_payment_transactions_tenant_id_transaction_reference)`, `INDEX (ix_payment_transactions_transaction_reference)` | Tenant-scoped transaction reference |
| `external_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_payment_transactions_external_reference)` | External transaction reference |
| `payment_provider` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_payment_transactions_payment_provider)` | Gateway provider identifier (e.g. razorpay, stripe) |
| `provider_transaction_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_payment_transactions_provider_transaction_reference)` | Non-secret provider transaction ID |
| `provider_authorization_reference` | `VARCHAR(100)` | `NULLABLE` | — | Non-secret provider auth ID |
| `transaction_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (transaction_type IN ('authorization', 'capture', 'payment', 'refund', 'void', 'adjustment'))`, `INDEX (ix_payment_transactions_transaction_type)` | Transaction type |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'processing', 'authorized', 'completed', 'failed', 'cancelled'))`, `INDEX (ix_payment_transactions_status)` | Transaction status |
| `amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (amount >= 0)` | Base transaction amount |
| `authorized_amount` | `NUMERIC(18,4)` | `NULLABLE` | `CHECK (authorized_amount IS NULL OR authorized_amount >= 0)` | Authorized amount |
| `captured_amount` | `NUMERIC(18,4)` | `NULLABLE` | `CHECK (captured_amount IS NULL OR captured_amount >= 0)` | Captured amount |
| `fee_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (fee_amount >= 0)` | Processing fee amount |
| `tax_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (tax_amount >= 0)` | Tax amount |
| `total_amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (total_amount >= 0)` | Total transaction amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | Currency code |
| `transaction_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_payment_transactions_created_at)` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `processed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Processing timestamp |
| `authorized_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Authorization timestamp |
| `captured_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Capture timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Failure timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Security & Provider References

- **Zero Plaintext Secrets**: Raw card numbers, CVV, PIN, OTP, API secret keys, or authorization tokens MUST NOT be stored in `transaction_metadata` or exposed in `__repr__`. Only non-secret provider references (e.g. `pay_12345`) are permitted.
- **Tenant Isolation**: `tenant_id` is mandatory and indexed on all records.
- **Numeric Precision**: Decimal `NUMERIC(18,4)` semantics are strictly enforced.
