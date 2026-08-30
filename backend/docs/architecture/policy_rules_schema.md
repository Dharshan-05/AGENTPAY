# AGENTPAY Policy Rules Schema Architecture (Phase 052)

## Executive Summary

This document formalizes the architectural specification and schema layout for `policy_rules` in **AGENTPAY** (`Phase 052`).

`policy_rules` represents deterministic rules belonging to a SecurityPolicy.

---

## 1. Schema Specifications (`policy_rules`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_policy_rules)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_policy_rules_tenant_id)` | Multi-tenancy isolation key |
| `security_policy_id` | `UUID` | `NOT NULL` | `FOREIGN KEY (fk_policy_rules_security_policy_id_security_policies) REFERENCES security_policies(id) ON DELETE RESTRICT`, `INDEX (ix_policy_rules_security_policy_id)` | Foreign key referencing security_policies |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_rules_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_policy_rules_merchant_id)` | Foreign key referencing merchants |
| `name` | `VARCHAR(255)` | `NOT NULL` | — | Rule title |
| `slug` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_policy_rules_tenant_id_security_policy_id_slug)` | Tenant + policy scoped unique slug |
| `description` | `VARCHAR(500)` | `NULLABLE` | — | Rule details |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'draft'`, `CHECK (status IN ('draft', 'active', 'inactive', 'disabled', 'archived'))`, `INDEX (ix_policy_rules_status)` | Rule status |
| `rule_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (rule_type IN ('threshold', 'allowlist', 'denylist', 'velocity', 'amount', 'frequency', 'geography', 'identity', 'agent_trust', 'merchant', 'product', 'custom'))`, `INDEX (ix_policy_rules_rule_type)` | Rule type classification |
| `priority` | `INTEGER` | `NOT NULL` | `DEFAULT 100`, `CHECK (priority >= 0)` | Rule precedence (lower = higher precedence) |
| `operator` | `VARCHAR(50)` | `NOT NULL` | `CHECK (operator IN ('eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'contains', 'not_contains', 'exists', 'not_exists'))` | Evaluation operator |
| `condition_payload` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret rule condition payload |
| `action` | `VARCHAR(50)` | `NOT NULL` | `CHECK (action IN ('allow', 'deny', 'challenge', 'review', 'alert', 'block', 'require_approval'))` | Primary rule action |
| `failure_action` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'deny'`, `CHECK (failure_action IN ('deny', 'allow', 'alert', 'review'))` | Fallback action upon evaluation error |
| `starts_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Rule activation start timestamp |
| `ends_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (ends_at IS NULL OR starts_at <= ends_at)` | Rule activation end timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Modification timestamp (UTC) |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft deletion timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `policy_rule.tenant_id == security_policy.tenant_id == merchant.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent security policies or merchants while rules exist.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `condition_payload` or exposed in `__repr__`.
