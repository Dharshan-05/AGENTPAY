# AGENTPAY Commerce Transactions Schema Architecture (Phase 049)

## Executive Summary

This document formalizes the architectural specification and schema layout for `commerce_transactions` in **AGENTPAY** (`Phase 049`).

`commerce_transactions` represents the financial transaction record for purchases, authorizations, captures, refunds, voids, and adjustments.

> **IMPORTANT Architectural Boundaries**:
> - `PurchaseIntent`: Buyer's declared intent.
> - `PurchasePlan`: Execution plan for the intent.
> - `CommerceTransaction`: Actual commerce/financial transaction record.

---

## 1. Schema Specifications (`commerce_transactions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_commerce_transactions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_commerce_transactions_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_commerce_transactions_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_merchant_id)` | Foreign key referencing merchants |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_commerce_transactions_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_agent_id)` | Foreign key referencing agents |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_commerce_transactions_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_commerce_transactions_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_offer_id)` | Foreign key referencing offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_commerce_transactions_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_commerce_transactions_purchase_plan_id_purchase_plans) REFERENCES purchase_plans(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_transactions_purchase_plan_id)` | Foreign key referencing purchase_plans |
| `transaction_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_commerce_transactions_tenant_id_transaction_reference)` | Tenant-scoped unique transaction reference |
| `external_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_commerce_transactions_external_reference)` | Optional external reference ID |
| `transaction_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (transaction_type IN ('purchase', 'authorization', 'capture', 'refund', 'void', 'adjustment'))`, `INDEX (ix_commerce_transactions_transaction_type)` | Transaction type classification |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'authorized', 'completed', 'failed', 'cancelled', 'refunded', 'partially_refunded'))`, `INDEX (ix_commerce_transactions_status)` | Transaction status |
| `quantity` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 1.000`, `CHECK (quantity > 0)` | Purchased item quantity |
| `amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (amount >= 0)` | Base transaction amount |
| `subtotal` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (subtotal >= 0)` | Transaction subtotal |
| `tax_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (tax_amount >= 0)` | Tax amount |
| `discount_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (discount_amount >= 0)` | Discount amount |
| `fee_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (fee_amount >= 0)` | Fee amount |
| `total_amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (total_amount >= 0)` | Total calculated amount |
| `refunded_amount` | `NUMERIC(18,4)` | `NOT NULL` | `DEFAULT 0.0000`, `CHECK (refunded_amount >= 0)`, `CHECK (refunded_amount <= total_amount)` | Total refunded amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | ISO 4217 currency code |
| `payment_provider` | `VARCHAR(100)` | `NULLABLE` | — | Non-secret payment provider name |
| `provider_transaction_reference` | `VARCHAR(100)` | `NULLABLE` | — | Non-secret provider reference |
| `provider_authorization_reference` | `VARCHAR(100)` | `NULLABLE` | — | Non-secret provider authorization reference |
| `metadata_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret metadata payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Modification timestamp (UTC) |
| `authorized_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Authorization timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Completion timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Failure timestamp |
| `cancelled_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Cancellation timestamp |
| `refunded_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Refund timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `commerce_transaction.tenant_id == merchant.tenant_id == agent.tenant_id == product.tenant_id`.
- **NUMERIC Precision**: All monetary values use `NUMERIC(18,4)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent entities while transaction records exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers (PAN), CVV, or private keys MUST NOT be stored in `metadata_payload` or exposed in `__repr__`.
