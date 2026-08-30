# AGENTPAY Database Integrity Specifications (Phase 060)

## Executive Summary

This document formalizes the overall database integrity standards, constraints, numeric precision rules, append-only policies, and security audits across all **38 application tables** in **AGENTPAY** (`Phase 060`).

---

## 1. Primary Keys & Multi-Tenancy

- **Primary Keys**: Every application table uses UUIDv7 primary keys (`id`).
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all tenant-scoped tables (`ix_<table>_tenant_id`). Cross-tenant relationship references fail validation.

---

## 2. Numeric Precision & Financial Rules

- **Financial / Money Fields**: `NUMERIC(18,4)` Decimal semantics (e.g. prices, amounts, tax, fees).
- **Quantity Fields**: `NUMERIC(18,3)` Decimal semantics.
- **Score / Probability Fields**: `NUMERIC(8,4)` Decimal semantics.
- **SHAP / XAI Prediction Values**: `NUMERIC(18,8)` Decimal semantics.
- **Prohibited Types**: `FLOAT` and `REAL` types are strictly prohibited across all database models.

---

## 3. Append-Only Audit

Event tables (`commerce_events`, `behaviour_events`, `inventory_events`) are strictly append-only:
- Mandatory `occurred_at` / `created_at` timestamp.
- `updated_at` and `deleted_at` are strictly prohibited on append-only event tables.

---

## 4. Security & Secret Protection

- Zero plaintext credentials, raw API keys, bearer tokens, passwords, card numbers (PAN), CVV, or private keys stored or exposed in `__repr__`, logs, or JSONB metadata payloads.
- JSONB columns contain non-secret structured metadata only.
