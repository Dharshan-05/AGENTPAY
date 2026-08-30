# AGENTPAY Purchase Intents Schema Architecture (Phase 047)

## Executive Summary

This document formalizes the architectural specification and schema layout for `purchase_intents` in **AGENTPAY** (`Phase 047`).

`purchase_intents` represents the buyer/agent's declared intention to purchase one or more products/offers.

> **IMPORTANT Architectural Boundary**: Purchase Intent != Commerce Transaction. Purchase intents represent declared buyer intent prior to plan formulation, policy evaluation, or payment execution.

---

## 1. Schema Specifications (`purchase_intents`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_purchase_intents)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_purchase_intents_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_intents_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_intents_merchant_id)` | Foreign key referencing merchants |
| `agent_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_intents_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_intents_agent_id)` | Foreign key referencing agents |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_purchase_intents_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_intents_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_purchase_intents_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_purchase_intents_offer_id)` | Foreign key referencing offers |
| `intent_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_purchase_intents_tenant_id_intent_reference)` | Tenant-scoped unique intent reference |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled'))`, `INDEX (ix_purchase_intents_status)` | Intent status |
| `quantity` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 1.000`, `CHECK (quantity > 0)` | Intended purchase quantity |
| `unit_price` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (unit_price >= 0)` | Unit price |
| `total_amount` | `NUMERIC(18,4)` | `NOT NULL` | `CHECK (total_amount >= 0)` | Total intent amount |
| `currency_code` | `VARCHAR(3)` | `NOT NULL` | `DEFAULT 'USD'` | ISO 4217 currency code |
| `requested_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Intent declaration timestamp (UTC) |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (expires_at IS NULL OR requested_at <= expires_at)` | Intent expiration timestamp |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | — | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor classification |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `intent_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret metadata payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `purchase_intent.tenant_id == merchant.tenant_id == agent.tenant_id == product.tenant_id == offer.tenant_id`.
- **NUMERIC Precision**: Monetary prices and totals use `NUMERIC(18,4)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent entities while active intents exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `intent_metadata` or exposed in `__repr__`.
