# AGENTPAY Database Schema Standards Architecture (Phase 020)

## Executive Summary

This document specifies the mandatory database schema standards for **AGENTPAY** database tables (`Phase 020`).

These standards govern data types, primary keys (UUIDv7), multi-tenancy (`tenant_id`), UTC timezone-aware timestamps, nullability, financial representation, soft deletion, and foreign key policies for all future domain schemas (Phase 021+).

---

## 1. Primary Keys & Multi-Tenancy Standards

- **Canonical Primary Key**: Every operational table MUST use `id UUID` as its primary key, generated via time-ordered **UUIDv7** (`Phase 011`).
- **Multi-Tenancy Readiness**: Domain tables belonging to a tenant MUST contain `tenant_id UUID NOT NULL`.
- **Prohibited Types**: `SERIAL`, `BIGSERIAL`, and auto-incrementing integer primary keys are prohibited for domain models.

---

## 2. Timestamps & Timezones

- **Timezone Awareness**: All timestamp columns MUST use `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`) in UTC.
- **Audit Columns**:
  - `created_at TIMESTAMPTZ NOT NULL`: Set automatically on row creation.
  - `updated_at TIMESTAMPTZ NOT NULL`: Updated automatically on row modification.
  - `deleted_at TIMESTAMPTZ NULL`: Set on soft deletion for operational entities.
- **Immutable Append-Only Records**: Audit logs, security events, and financial ledger records are append-only and do NOT use `updated_at` or `deleted_at`.

---

## 3. Financial & Quantity Data Types

- **Financial Monetary Amounts**: MUST use exact `NUMERIC(precision, scale)` or `DECIMAL` types paired with `currency_code` (ISO 4217). `FLOAT` and `REAL` types are strictly prohibited for money.
- **Quantities**: Exact discrete quantities use `INTEGER` or `BIGINT`; fractional quantities use `NUMERIC(precision, scale)`.

---

## 4. Nullability, Constraints & Foreign Key Policies

- **Default Nullability**: Columns are `NOT NULL` by default unless `NULL` has explicit business semantics.
- **Foreign Key Delete Policies**:
  - Financial, security, and audit records MUST enforce `ON DELETE RESTRICT` or `ON DELETE NO ACTION` to prevent accidental cascading data loss.
  - Operational child records may use explicitly reviewed `ON DELETE CASCADE` or `ON DELETE SET NULL`.
- **JSONB Usage**: PostgreSQL `JSONB` is reserved for dynamic metadata, AI explanation payloads, and provider metadata. Core queryable domain attributes must remain relational columns.
