# AGENTPAY Payment Idempotency Schema Architecture (Phase 067)

## Executive Summary

This document formalizes the architectural specification and schema layout for `payment_idempotency_keys` in **AGENTPAY** (`Phase 067`).

`payment_idempotency_keys` provides durable, tenant-scoped idempotency protection for payment processing operations.

---

## 1. Schema Specifications (`payment_idempotency_keys`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_payment_idempotency_keys)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_payment_idempotency_keys_tenant_id)` | Multi-tenancy isolation key |
| `idempotency_key` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_payment_idempotency_keys_tenant_key)`, `INDEX (ix_payment_idempotency_keys_idempotency_key)` | Tenant-scoped idempotency key |
| `operation_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (operation_type IN ('create_order', 'authorize', 'capture', 'refund', 'cancel', 'payment', 'retry', 'webhook'))`, `INDEX (ix_payment_idempotency_keys_operation_type)` | Operation type classification |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_payment_idempotency_keys_request_id)` | Correlation request ID |
| `resource_type` | `VARCHAR(100)` | `NULLABLE` | — | Target resource entity type |
| `resource_id` | `UUID` | `NULLABLE` | `INDEX (ix_payment_idempotency_keys_resource_id)` | Target resource UUID |
| `request_hash` | `VARCHAR(64)` | `NULLABLE` | — | Non-secret SHA-256 request payload hash |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'expired', 'conflict'))`, `INDEX (ix_payment_idempotency_keys_status)` | Idempotency lifecycle state |
| `response_code` | `INTEGER` | `NULLABLE` | — | HTTP or internal status response code |
| `response_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret response metadata payload |
| `first_seen_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | First arrival timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Processing completion timestamp |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_payment_idempotency_keys_expires_at)` | Key expiration timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |

---

## 2. Security Controls & Guidelines

- **Zero Secrets Storage**: API keys, bearer tokens, passwords, card numbers, CVV, or authorization headers MUST NOT be stored in `response_metadata` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
- **Redaction Policy**: `request_hash`, `response_metadata`, and `idempotency_key` are redacted from `__repr__`.
