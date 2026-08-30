# AGENTPAY Commerce Events Schema Architecture (Phase 050)

## Executive Summary

This document formalizes the architectural specification and schema layout for `commerce_events` in **AGENTPAY** (`Phase 050`).

`commerce_events` represents an immutable, append-only lifecycle event describing a commerce transaction transition.

---

## 1. Schema Specifications (`commerce_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_commerce_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_commerce_events_tenant_id)` | Multi-tenancy isolation key |
| `transaction_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_commerce_events_transaction_id_commerce_transactions) REFERENCES commerce_transactions(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_events_transaction_id)` | Foreign key referencing commerce_transactions |
| `merchant_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_commerce_events_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_events_merchant_id)` | Foreign key referencing merchants |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_commerce_events_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_commerce_events_agent_id)` | Foreign key referencing agents |
| `event_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_commerce_events_tenant_id_event_reference)` | Tenant-scoped unique event reference |
| `event_type` | `VARCHAR(100)` | `NOT NULL` | `CHECK (event_type IN ('transaction', 'authorization', 'capture', 'refund', 'adjustment', 'lifecycle'))`, `INDEX (ix_commerce_events_event_type)` | Event type classification |
| `event_action` | `VARCHAR(100)` | `NOT NULL` | `CHECK (event_action IN ('created', 'requested', 'approved', 'completed', 'failed', 'cancelled', 'refunded'))` | Specific event action |
| `event_result` | `VARCHAR(50)` | `NULLABLE` | `CHECK (event_result IS NULL OR event_result IN ('success', 'failure', 'pending'))` | Outcome state |
| `sequence_number` | `BIGINT` | `NOT NULL` | `UNIQUE (uq_commerce_events_transaction_id_sequence_number)` | Deterministic sequence number per transaction |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | — | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor classification |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `event_metadata` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret metadata payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_commerce_events_occurred_at)` | Occurrence timestamp (UTC) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp (UTC) |

---

## 2. Append-Only & Integrity Rules

- **Append-Only Structure**: `commerce_events` includes `occurred_at` and `created_at`. `updated_at` and `deleted_at` are strictly prohibited.
- **Tenant Isolation**: `commerce_event.tenant_id == commerce_transaction.tenant_id == merchant.tenant_id`.
- **Deterministic Ordering**: `uq_commerce_events_transaction_id_sequence_number` guarantees strict sequential order per transaction.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent transactions while event history exists.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `event_metadata` or exposed in `__repr__`.
