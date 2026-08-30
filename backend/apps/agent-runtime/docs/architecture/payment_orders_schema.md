# AGENTPAY Payment Orders Schema Architecture (Phase 061)

## Executive Summary

This document formalizes the architectural specification and schema layout for `payment_orders` in **AGENTPAY** (`Phase 061`).

`payment_orders` provides a durable financial order boundary between purchase intents/plans, merchants, agents, products/offers, and payment processing attempts.

---

## 1. Schema Specifications (`payment_orders`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_payment_orders)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_payment_orders_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_merchant_id)` | FK to merchants |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_agent_id)` | FK to agents |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_product_id)` | FK to products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_offer_id)` | FK to offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_purchase_intent_id)` | FK to purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_orders_purchase_plan_id)` | FK to purchase_plans |
| `order_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_payment_orders_tenant_id_order_reference)`, `INDEX (ix_payment_orders_order_reference)` | Tenant-scoped order reference |
| `external_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_payment_orders_external_reference)` | Optional external system reference |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'created'`, `CHECK (status IN ('created', 'pending', 'processing', 'authorized', 'completed', 'failed', 'cancelled', 'expired'))`, `INDEX (ix_payment_orders_status)` | Order lifecycle status |
| `amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (amount >= 0)` | Base financial order amount |
| `subtotal` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (subtotal >= 0)` | Subtotal amount |
| `tax_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (tax_amount >= 0)` | Tax amount |
| `discount_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (discount_amount >= 0)` | Discount amount |
| `fee_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (fee_amount >= 0)` | Processing fee amount |
| `total_amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (total_amount >= 0)` | Total payment order amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | ISO-4217 currency code |
| `quantity` | `NUMERIC(18,3)` | `NULLABLE` | `DEFAULT 1.000`, `CHECK (quantity IS NULL OR quantity >= 0)` | Quantity ordered |
| `order_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured metadata |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_payment_orders_created_at)` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Order expiration timestamp |
| `authorized_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Order authorization timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Order completion timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Order failure timestamp |
| `cancelled_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Order cancellation timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Security & Financial Precision Controls

- **Tenant Isolation**: `tenant_id` is mandatory and indexed on all records.
- **Foreign Keys**: All foreign key relationships enforce `ON DELETE RESTRICT`.
- **Zero Payment Secrets**: Credit card numbers, CVV, PIN, OTP, raw API keys, or private authorization tokens MUST NOT be stored in `order_metadata` or exposed in `__repr__`.
- **Numeric Precision**: Monetary values use Decimal `NUMERIC(18,4)` and quantities use `NUMERIC(18,3)`. `FLOAT` or `REAL` types are strictly prohibited.
