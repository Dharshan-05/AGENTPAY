# AGENTPAY Policy Evaluation Schema Architecture (Phase 053)

## Executive Summary

This document formalizes the architectural specification and schema layout for `policy_evaluations` in **AGENTPAY** (`Phase 053`).

`policy_evaluations` represents the result of evaluating one security policy/rule against a concrete agentic commerce/payment operation.

> **IMPORTANT Scope Lock**: This phase defines policy evaluation history only. Security violations, risk signals, fraud predictions, and XAI/SHAP explanations belong to future phases (Phases 055–058) and are intentionally absent.

---

## 1. Schema Specifications (`policy_evaluations`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_policy_evaluations)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_policy_evaluations_tenant_id)` | Multi-tenancy isolation key |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_security_policy_id_security_policies) REFERENCES security_policies(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_security_policy_id)` | Foreign key referencing security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_policy_rule_id_policy_rules) REFERENCES policy_rules(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_policy_rule_id)` | Foreign key referencing policy_rules |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_merchant_id)` | Foreign key referencing merchants |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_agent_id)` | Foreign key referencing agents |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_offer_id)` | Foreign key referencing offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_purchase_plan_id_purchase_plans) REFERENCES purchase_plans(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_purchase_plan_id)` | Foreign key referencing purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_policy_evaluations_commerce_transaction_id_commerce_transactions) REFERENCES commerce_transactions(id) ON DELETE RESTRICT`, `INDEX (ix_policy_evaluations_commerce_transaction_id)` | Foreign key referencing commerce_transactions |
| `evaluation_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_policy_evaluations_tenant_id_evaluation_reference)` | Tenant-scoped evaluation reference |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_policy_evaluations_request_id)` | Distributed request tracing ID |
| `evaluation_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (evaluation_type IN ('authorization', 'transaction', 'fraud', 'risk', 'compliance', 'spending', 'access', 'agent', 'commerce'))`, `INDEX (ix_policy_evaluations_evaluation_type)` | Evaluation classification |
| `decision` | `VARCHAR(50)` | `NOT NULL` | `CHECK (decision IN ('allow', 'deny', 'challenge', 'review', 'alert', 'block', 'require_approval'))`, `INDEX (ix_policy_evaluations_decision)` | Evaluation decision |
| `result` | `VARCHAR(50)` | `NOT NULL` | `CHECK (result IN ('success', 'failure', 'error', 'skipped'))` | Evaluation result |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'completed'`, `CHECK (status IN ('pending', 'completed', 'failed', 'expired', 'cancelled'))`, `INDEX (ix_policy_evaluations_status)` | Lifecycle status |
| `priority` | `INTEGER` | `NOT NULL` | `DEFAULT 100`, `CHECK (priority >= 0)` | Evaluation priority |
| `evaluation_version` | `INTEGER` | `NOT NULL` | `DEFAULT 1`, `CHECK (evaluation_version > 0)` | Evaluation schema/engine version |
| `condition_result` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret rule evaluation output facts |
| `evaluation_context` | `JSONB` | `NOT NULL` | `DEFAULT '{}'` | Non-secret evaluation context |
| `failure_code` | `VARCHAR(100)` | `NULLABLE` | — | Machine-readable failure code |
| `failure_message` | `VARCHAR(500)` | `NULLABLE` | — | Non-sensitive error message |
| `evaluated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_policy_evaluations_evaluated_at)` | Timestamp evaluation occurred |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Integrity & Security Rules

- **Tenant Isolation**: `policy_evaluation.tenant_id == security_policy.tenant_id == merchant.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` prevents deletion of parent entities while evaluation history exists.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `condition_result` / `evaluation_context` or exposed in `__repr__`.
