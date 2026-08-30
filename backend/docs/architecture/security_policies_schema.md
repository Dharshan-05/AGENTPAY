# AGENTPAY Security Policies Schema Architecture (Phase 051)

## Executive Summary

This document formalizes the architectural specification and schema layout for `security_policies` in **AGENTPAY** (`Phase 051`).

`security_policies` defines tenant-scoped security, risk, compliance, spending, and authorization policies.

> **IMPORTANT Scope Lock**: This phase defines policy configuration and rules only. Policy evaluation, risk engine execution, security violations, and XAI explanations belong to future phases (Phases 053–058) and are intentionally absent.

---

## 1. Schema Specifications (`security_policies`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_security_policies)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_security_policies_tenant_id)` | Multi-tenancy isolation key |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_policies_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_security_policies_merchant_id)` | Foreign key referencing merchants |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Human-readable policy title |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_security_policies_tenant_id_slug)` | Tenant-scoped unique slug |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Policy details |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'draft'`, `CHECK (status IN ('draft', 'active', 'inactive', 'suspended', 'archived'))`, `INDEX (ix_security_policies_status)` | Policy lifecycle status |
| `policy_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (policy_type IN ('authorization', 'transaction', 'fraud', 'risk', 'compliance', 'spending', 'access', 'agent', 'commerce'))`, `INDEX (ix_security_policies_policy_type)` | Policy type classification |
| `priority` | `INTEGER` | `NOT NULL` | `DEFAULT 100`, `CHECK (priority >= 0)` | Evaluation priority (lower = higher precedence) |
| `enforcement_mode` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'enforce'`, `CHECK (enforcement_mode IN ('enforce', 'monitor', 'warn', 'block'))` | Policy enforcement mode |
| `version` | `INTEGER` | `NOT NULL` | `DEFAULT 1`, `CHECK (version >= 1)` | Policy version number |
| `starts_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Activation start timestamp |
| `ends_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (ends_at IS NULL OR starts_at <= ends_at)` | Activation end timestamp |
| `configuration` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret configuration payload |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `security_policy.tenant_id == merchant.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent merchants while policy records exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `configuration` or exposed in `__repr__`.
