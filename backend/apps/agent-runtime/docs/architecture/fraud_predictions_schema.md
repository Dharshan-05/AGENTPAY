# AGENTPAY Fraud Predictions Schema Architecture (Phase 057)

## Executive Summary

This document formalizes the architectural specification and schema layout for `fraud_predictions` in **AGENTPAY** (`Phase 057`).

`fraud_predictions` stores fraud-model predictions generated for AGENTPAY commerce, payment, agent, and security activities.

---

## 1. Schema Specifications (`fraud_predictions`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_fraud_predictions)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_fraud_predictions_tenant_id)` | Multi-tenancy isolation key |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_security_policy_id)` | FK to security_policies |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_policy_rule_id)` | FK to policy_rules |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_policy_evaluation_id)` | FK to policy_evaluations |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_security_violation_id)` | FK to security_violations |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_risk_signal_id)` | FK to risk_signals |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_agent_id)` | FK to agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_merchant_id)` | FK to merchants |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_product_id)` | FK to products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_offer_id)` | FK to offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_purchase_intent_id)` | FK to purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_purchase_plan_id)` | FK to purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_fraud_predictions_commerce_transaction_id)` | FK to commerce_transactions |
| `prediction_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_fraud_predictions_tenant_id_prediction_reference)` | Tenant-scoped prediction reference |
| `model_reference` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_fraud_predictions_model_reference)` | ML model identifier/name |
| `model_version` | `VARCHAR(50)` | `NOT NULL` | — | ML model version string |
| `prediction_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (prediction_type IN ('transaction', 'payment', 'purchase', 'account', 'agent', 'merchant', 'identity', 'behaviour', 'commerce', 'custom'))`, `INDEX (ix_fraud_predictions_prediction_type)` | Classification type |
| `prediction_status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'completed'`, `CHECK (prediction_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled'))`, `INDEX (ix_fraud_predictions_prediction_status)` | Lifecycle status |
| `prediction_label` | `VARCHAR(50)` | `NOT NULL` | `CHECK (prediction_label IN ('legitimate', 'suspicious', 'fraud', 'unknown'))`, `INDEX (ix_fraud_predictions_prediction_label)` | Inferred classification label |
| `fraud_probability` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (fraud_probability BETWEEN 0 AND 1)` | Fraud probability score |
| `legitimate_probability` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (legitimate_probability BETWEEN 0 AND 1)` | Legitimate probability score |
| `risk_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (risk_score BETWEEN 0 AND 100)` | Risk score (0..100) |
| `confidence_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (confidence_score BETWEEN 0 AND 1)` | Confidence score (0..1) |
| `feature_count` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (feature_count >= 0)` | Feature count evaluated |
| `feature_snapshot` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret model features snapshot |
| `prediction_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret prediction context |
| `prediction_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_fraud_predictions_request_id)` | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor classification |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `predicted_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_fraud_predictions_predicted_at)` | Prediction timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Integrity & Security Controls

- **Tenant Isolation**: Every `FraudPrediction` belongs to exactly one tenant.
- **Foreign Keys**: 12 optional foreign keys using `ON DELETE RESTRICT`.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in `feature_snapshot`, `prediction_context`, or `prediction_metadata`, or exposed in `__repr__`.
- **Numeric Precision**: All scores use Decimal `NUMERIC(8,4)` semantics. `FLOAT` or `REAL` types are strictly prohibited.
