# AGENTPAY Security Violations Schema Architecture (Phase 055)

## Executive Summary

This document formalizes the architectural specification and schema layout for `security_violations` in **AGENTPAY** (`Phase 055`).

`security_violations` represents detected security-policy, authorization, authentication, fraud, risk, compliance, and agent-security violations produced during agentic commerce activity.

> **IMPORTANT Scope Lock**: This phase defines security violations and associated risk signals only. Fraud predictions and XAI/SHAP explanations belong to future phases (Phases 057–058) and are intentionally absent.

---

## 1. Schema Specifications (`security_violations`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_security_violations)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_security_violations_tenant_id)` | Multi-tenancy isolation key |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_security_policy_id_security_policies) REFERENCES security_policies(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_security_policy_id)` | Foreign key referencing security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_policy_rule_id_policy_rules) REFERENCES policy_rules(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_policy_rule_id)` | Foreign key referencing policy_rules |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_policy_evaluation_id_policy_evaluations) REFERENCES policy_evaluations(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_policy_evaluation_id)` | Foreign key referencing policy_evaluations |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_agent_id)` | Foreign key referencing agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_offer_id)` | Foreign key referencing offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_purchase_plan_id_purchase_plans) REFERENCES purchase_plans(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_purchase_plan_id)` | Foreign key referencing purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_security_violations_commerce_transaction_id_commerce_transactions) REFERENCES commerce_transactions(id) ON DELETE RESTRICT`, `INDEX (ix_security_violations_commerce_transaction_id)` | Foreign key referencing commerce_transactions |
| `violation_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_security_violations_tenant_id_violation_reference)`, `INDEX (ix_security_violations_violation_reference)` | Tenant-scoped violation reference |
| `violation_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (violation_type IN ('authentication', 'authorization', 'policy', 'fraud', 'risk', 'compliance', 'spending', 'access', 'agent', 'commerce', 'transaction', 'inventory', 'credential', 'tenant_isolation', 'system'))`, `INDEX (ix_security_violations_violation_type)` | Violation classification |
| `severity` | `VARCHAR(50)` | `NOT NULL` | `CHECK (severity IN ('low', 'medium', 'high', 'critical'))`, `INDEX (ix_security_violations_severity)` | Severity level |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'open'`, `CHECK (status IN ('open', 'investigating', 'confirmed', 'resolved', 'dismissed', 'false_positive'))`, `INDEX (ix_security_violations_status)` | Investigation status |
| `detection_source` | `VARCHAR(50)` | `NOT NULL` | `CHECK (detection_source IN ('policy_engine', 'rule_engine', 'risk_engine', 'fraud_engine', 'authentication', 'authorization', 'agent_runtime', 'system', 'manual'))` | Engine or origin detecting violation |
| `title` | `VARCHAR(255)` | `NOT NULL` | — | Short human-readable summary |
| `description` | `TEXT` | `NULLABLE` | — | Detailed explanation |
| `violation_code` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_security_violations_violation_code)` | Machine-readable violation code |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_security_violations_request_id)` | Distributed request correlation ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Type of actor triggering violation |
| `actor_id` | `UUID` | `NULLABLE` | — | UUID of actor triggering violation |
| `risk_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (risk_score >= 0 AND risk_score <= 100)` | Quantified risk score |
| `impact_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (impact_score >= 0 AND impact_score <= 100)` | Quantified impact score |
| `violation_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured context |
| `evidence_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured evidence |
| `resolution_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret resolution context |
| `detected_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_security_violations_detected_at)` | Timestamp violation detected |
| `acknowledged_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (acknowledged_at IS NULL OR detected_at <= acknowledged_at)` | Timestamp violation acknowledged |
| `resolved_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (resolved_at IS NULL OR detected_at <= resolved_at)` | Timestamp violation resolved |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Integrity & Security Controls

- **Tenant Isolation**: `security_violation.tenant_id == related_entity.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` on all 10 foreign keys.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `violation_context`, `evidence_payload`, or `resolution_payload`, or exposed in `__repr__`.
- **Numeric Precision**: `risk_score` and `impact_score` use `NUMERIC(8,4)` Decimal. `FLOAT` or `REAL` types are strictly prohibited.
- **Scope Lock Boundary**: Fraud predictions and XAI / SHAP explanations are NOT implemented.
