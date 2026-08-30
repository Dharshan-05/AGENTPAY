# AGENTPAY Payment Events Schema Architecture (Phase 063)

## Executive Summary

This document formalizes the architectural specification and schema layout for `payment_events` in **AGENTPAY** (`Phase 063`).

`payment_events` represents the immutable append-only event history for payment processing in AGENTPAY.

---

## 1. Schema Specifications (`payment_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_payment_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_payment_events_tenant_id)` | Multi-tenancy isolation key |
| `payment_transaction_id` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_events_payment_transaction_id)` | FK to payment_transactions |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_payment_events_payment_order_id)` | FK to payment_orders |
| `event_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_payment_events_tenant_id_event_reference)` | Tenant-scoped event reference |
| `event_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (event_type IN ('payment', 'authorization', 'capture', 'failure', 'cancellation', 'lifecycle'))`, `INDEX (ix_payment_events_event_type)` | Event classification type |
| `event_action` | `VARCHAR(50)` | `NOT NULL` | `CHECK (event_action IN ('created', 'requested', 'processing', 'authorized', 'completed', 'failed', 'cancelled'))`, `INDEX (ix_payment_events_event_action)` | Event lifecycle action |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `CHECK (event_result IN ('success', 'failure', 'pending'))`, `INDEX (ix_payment_events_event_result)` | Outcome result |
| `sequence_number` | `BIGINT` | `NOT NULL` | `CHECK (sequence_number > 0)`, `UNIQUE (uq_payment_events_transaction_sequence)` | Transaction sequence number |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_payment_events_request_id)` | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor type |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `event_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_payment_events_occurred_at)` | Event occurrence timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Append-Only Integrity & Security Controls

- **Strictly Append-Only**: `payment_events` contains `occurred_at` and `created_at` ONLY. `updated_at` and `deleted_at` ARE STRICTLY PROHIBITED.
- **Deterministic Ordering**: `sequence_number` enforces strict per-transaction sequence ordering (`uq_payment_events_transaction_sequence`).
- **Tenant Isolation**: `tenant_id` is mandatory and indexed on all records.
- **Zero Payment Secrets**: Credit card numbers, CVV, PIN, OTP, raw API keys, or private authorization tokens MUST NOT be stored in `event_metadata` or exposed in `__repr__`.
