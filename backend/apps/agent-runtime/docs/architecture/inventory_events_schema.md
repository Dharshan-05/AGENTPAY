# AGENTPAY Inventory Events Schema Architecture (Phase 045)

## Executive Summary

This document formalizes the architectural specification and schema layout for `inventory_events` in **AGENTPAY** (`Phase 045`).

`inventory_events` provides append-only tracking of physical and reserved inventory stock movements, quantity deltas, and state transitions.

---

## 1. Schema Specifications (`inventory_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_inventory_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_inventory_events_tenant_id)` | Multi-tenancy isolation key |
| `inventory_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_events_inventory_id_inventory) REFERENCES inventory(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_events_inventory_id)` | Foreign key referencing inventory |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_events_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_events_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_inventory_events_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_inventory_events_product_id)` | Foreign key referencing products |
| `event_type` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_inventory_events_event_type)` | Event classification |
| `event_action` | `VARCHAR(100)` | `NOT NULL` | — | Specific event action |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'` | Event outcome state |
| `quantity_delta` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 0.000` | Stock quantity change |
| `quantity_before` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 0.000`, `CHECK (quantity_before >= 0)` | Stock quantity prior to event |
| `quantity_after` | `NUMERIC(18,3)` | `NOT NULL` | `DEFAULT 0.000`, `CHECK (quantity_after >= 0)` | Stock quantity post event |
| `reserved_quantity_delta` | `NUMERIC(18,3)` | `NULLABLE` | — | Reserved stock delta |
| `reserved_quantity_before` | `NUMERIC(18,3)` | `NULLABLE` | — | Reserved stock prior to event |
| `reserved_quantity_after` | `NUMERIC(18,3)` | `NULLABLE` | — | Reserved stock post event |
| `reference_type` | `VARCHAR(100)` | `NULLABLE` | — | External reference entity type |
| `reference_id` | `UUID` | `NULLABLE` | — | External reference UUID |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | — | Request correlation ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor classification |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `event_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Safe metadata payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_inventory_events_occurred_at)` | Event occurrence timestamp (UTC) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Integrity & Security Rules

- **Append-Only**: `inventory_events` contains `occurred_at` and `created_at`. `updated_at` and `deleted_at` are strictly prohibited.
- **Tenant Isolation**: `inventory_events.tenant_id == inventory.tenant_id == merchants.tenant_id == products.tenant_id`.
- **NUMERIC Precision**: Quantities use `NUMERIC(18,3)` (Decimal). `FLOAT` or `REAL` types are strictly PROHIBITED.
- **Quantity Consistency**: `ck_inventory_events_quantity_after_consistency` enforces `quantity_after = quantity_before + quantity_delta`.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, or private keys MUST NOT be stored in `event_metadata` or exposed in `__repr__`.
