# AGENTPAY Risk Signals Schema Architecture (Phase 056)

## Executive Summary

This document formalizes the architectural specification and schema layout for `risk_signals` in **AGENTPAY** (`Phase 056`).

`risk_signals` represents normalized risk indicators produced by the AGENTPAY security/risk pipeline.

> **IMPORTANT Scope Lock**: This phase defines risk signals and security violations only. Fraud predictions and XAI/SHAP explanations belong to future phases (Phases 057–058) and are intentionally absent.

---

## 1. Schema Specifications (`risk_signals`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_risk_signals)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_risk_signals_tenant_id)` | Multi-tenancy isolation key |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_security_policy_id_security_policies) REFERENCES security_policies(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_security_policy_id)` | Foreign key referencing security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_policy_rule_id_policy_rules) REFERENCES policy_rules(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_policy_rule_id)` | Foreign key referencing policy_rules |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_policy_evaluation_id_policy_evaluations) REFERENCES policy_evaluations(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_policy_evaluation_id)` | Foreign key referencing policy_evaluations |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_security_violation_id_security_violations) REFERENCES security_violations(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_security_violation_id)` | Foreign key referencing security_violations |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_agent_id_agents) REFERENCES agents(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_agent_id)` | Foreign key referencing agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_merchant_id_merchants) REFERENCES merchants(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_merchant_id)` | Foreign key referencing merchants |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_product_id_products) REFERENCES products(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_product_id)` | Foreign key referencing products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_offer_id_offers) REFERENCES offers(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_offer_id)` | Foreign key referencing offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_purchase_intent_id_purchase_intents) REFERENCES purchase_intents(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_purchase_intent_id)` | Foreign key referencing purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_purchase_plan_id_purchase_plans) REFERENCES purchase_plans(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_purchase_plan_id)` | Foreign key referencing purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY (fk_risk_signals_commerce_transaction_id_commerce_transactions) REFERENCES commerce_transactions(id) ON DELETE RESTRICT`, `INDEX (ix_risk_signals_commerce_transaction_id)` | Foreign key referencing commerce_transactions |
| `signal_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_risk_signals_tenant_id_signal_reference)` | Tenant-scoped signal reference |
| `signal_code` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_risk_signals_signal_code)` | Machine-readable signal code |
| `signal_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (signal_type IN ('velocity', 'amount', 'frequency', 'authentication', 'authorization', 'behaviour', 'fraud', 'device', 'identity', 'agent_trust', 'merchant', 'product', 'inventory', 'transaction', 'policy', 'compliance', 'geography', 'anomaly', 'spending', 'custom'))`, `INDEX (ix_risk_signals_signal_type)` | Signal classification |
| `signal_source` | `VARCHAR(50)` | `NOT NULL` | `CHECK (signal_source IN ('policy_engine', 'rule_engine', 'risk_engine', 'fraud_engine', 'behaviour_engine', 'authentication', 'authorization', 'agent_runtime', 'system', 'manual'))` | Origin producing signal |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'active'`, `CHECK (status IN ('active', 'inactive', 'expired', 'suppressed', 'resolved'))`, `INDEX (ix_risk_signals_status)` | Active/lifecycle status |
| `severity` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'low'`, `CHECK (severity IN ('low', 'medium', 'high', 'critical'))`, `INDEX (ix_risk_signals_severity)` | Severity level |
| `risk_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (risk_score >= 0 AND risk_score <= 100)` | Quantified risk score |
| `confidence_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (confidence_score >= 0 AND confidence_score <= 1)` | Signal confidence |
| `signal_value` | `NUMERIC(18,6)` | `NULLABLE` | — | Numeric value of signal |
| `signal_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured context |
| `evidence_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret structured evidence |
| `metadata_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_risk_signals_request_id)` | Distributed request correlation ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Type of actor producing signal |
| `actor_id` | `UUID` | `NULLABLE` | — | UUID of actor producing signal |
| `source_reference` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_risk_signals_source_reference)` | External/origin signal reference |
| `observed_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_risk_signals_observed_at)` | Timestamp signal observed |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE` | `CHECK (expires_at IS NULL OR observed_at <= expires_at)` | Signal expiration timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Integrity & Security Controls

- **Tenant Isolation**: `risk_signal.tenant_id == related_entity.tenant_id`.
- **Foreign Key Protection**: `ON DELETE RESTRICT` on all 11 foreign keys.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `signal_context`, `evidence_payload`, or `metadata_payload`, or exposed in `__repr__`.
- **Numeric Precision**: `risk_score` (8,4), `confidence_score` (8,4), and `signal_value` (18,6) use Decimal semantics. `FLOAT` or `REAL` types are strictly prohibited.
- **Scope Lock Boundary**: Fraud predictions and XAI / SHAP explanations are NOT implemented.
