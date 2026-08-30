# AGENTPAY Purchase Plans Schema Architecture (Phase 048)

## Executive Summary

This document formalizes the architectural specification and schema layout for `purchase_plans` in **AGENTPAY** (`Phase 048`).

`purchase_plans` represents structured purchase execution planning derived from purchase intents.

> **IMPORTANT Architectural Boundary**: Purchase Plan != Commerce Transaction. Purchase plans describe HOW an intent is planned for execution prior to payment processing or transaction execution.

---

## 1. Schema Specifications (`purchase_plans`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_purchase_plans)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_purchase_plans_tenant_id)` | Multi-tenancy isolation key |
| `purchase_intent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_plans_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_plans_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_plans_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_plans_merchant_id)` | Foreign key referencing merchants |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_plans_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_plans_agent_id)` | Foreign key referencing agents |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_plans_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_plans_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_purchase_plans_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_plans_offer_id)` | Foreign key referencing offers |
| `plan_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_purchase_plans_tenant_id_plan_reference)` | Tenant-scoped unique plan reference |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'draft'`, `CHECK (status IN ('draft', 'ready', 'executing', 'completed', 'failed', 'cancelled', 'expired'))`, `INDEX (ix_purchase_plans_status)` | Plan status |
| `quantity` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 1.000`, `CHECK (quantity > 0)` | Planned purchase quantity |
| `unit_price` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (unit_price >= 0)` | Unit price |
| `subtotal` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (subtotal >= 0)` | Subtotal amount |
| `total_amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (total_amount >= 0)` | Total plan amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | ISO 4217 currency code |
| `planned_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Planning timestamp (UTC) |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (expires_at IS NULL OR planned_at <= expires_at)` | Plan expiration timestamp |
| `plan_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret metadata payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `purchase_plan.tenant_id == purchase_intent.tenant_id == merchant.tenant_id == agent.tenant_id == product.tenant_id == offer.tenant_id`.
- **NUMERIC Precision**: Monetary values use `NUMERIC(18,4)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent entities while active plans exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `plan_metadata` or exposed in `__repr__`.
