# AGENTPAY Razorpay Webhook Events Schema Architecture (Phase 064)

## Executive Summary

This document formalizes the architectural specification and schema layout for `razorpay_webhook_events` in **AGENTPAY** (`Phase 064`).

`razorpay_webhook_events` represents inbound Razorpay webhook notifications received at the boundary of AGENTPAY.

> [!IMPORTANT]
> **Domain Distinction**: `payment_events` represents AGENTPAY's internal append-only payment lifecycle event log. `razorpay_webhook_events` represents raw, untrusted external webhook payload notifications received from Razorpay. Both models are strictly segregated.

> [!CAUTION]
> **WEBHOOK PAYLOAD = UNTRUSTED EXTERNAL DATA**: Webhook payloads received from external boundaries must never store API secret keys, webhook signing secrets, card numbers, CVV, PIN, or authorization tokens.

---

## 1. Schema Specifications (`razorpay_webhook_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_razorpay_webhook_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_razorpay_webhook_events_tenant_id)` | Multi-tenancy isolation key |
| `payment_order_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_razorpay_webhook_events_payment_order_id)` | FK to payment_orders |
| `payment_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_razorpay_webhook_events_payment_transaction_id)` | FK to payment_transactions |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_razorpay_webhook_events_merchant_id)` | FK to merchants |
| `provider_event_id` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_razorpay_webhook_events_tenant_provider_event)`, `INDEX (ix_razorpay_webhook_events_provider_event_id)` | Razorpay event ID |
| `event_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_razorpay_webhook_events_tenant_event_reference)`, `INDEX (ix_razorpay_webhook_events_event_reference)` | Internal event reference |
| `event_type` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_razorpay_webhook_events_event_type)` | Razorpay event type (e.g. payment.captured) |
| `processing_status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'received'`, `CHECK (processing_status IN ('received', 'processing', 'processed', 'failed', 'ignored'))`, `INDEX (ix_razorpay_webhook_events_processing_status)` | Processing lifecycle state |
| `verification_status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'pending'`, `CHECK (verification_status IN ('pending', 'verified', 'failed', 'skipped'))`, `INDEX (ix_razorpay_webhook_events_verification_status)` | Signature verification state |
| `signature_verified` | `BOOLEAN` | `NOT NULL` | `DEFAULT FALSE` | Verification boolean flag |
| `event_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Untrusted JSONB payload (Redacted from `__repr__`) |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_razorpay_webhook_events_request_id)` | Correlation request ID |
| `processing_error` | `VARCHAR(1000)` | `NULLABLE` | — | Error diagnostic message |
| `received_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_razorpay_webhook_events_received_at)` | Arrival timestamp |
| `processed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Processing completion timestamp |
| `verified_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Signature verification timestamp |
| `failed_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Failure timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |

---

## 2. Security Controls & Secrets Policy

- **Zero Secrets Storage**: `webhook_secret`, `razorpay_secret`, `signing_secret`, API keys, card PAN, CVV, or passwords are strictly prohibited.
- **Tenant Isolation**: Mandatory indexed `tenant_id` prevents cross-tenant access.
- **Payload Redaction**: `event_payload` is excluded from `__repr__`.
