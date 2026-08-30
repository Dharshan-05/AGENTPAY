# AGENTPAY XAI / SHAP Explanations Schema Architecture (Phase 058)

## Executive Summary

This document formalizes the architectural specification and schema layout for `xai_explanations` in **AGENTPAY** (`Phase 058`).

`xai_explanations` stores explainable-AI output (SHAP values, feature importance, reasoning summaries) associated with fraud/risk predictions.

---

## 1. Schema Specifications (`xai_explanations`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_xai_explanations)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_xai_explanations_tenant_id)` | Multi-tenancy isolation key |
| `fraud_prediction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_fraud_prediction_id)` | FK to fraud_predictions |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_risk_signal_id)` | FK to risk_signals |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_security_violation_id)` | FK to security_violations |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_policy_evaluation_id)` | FK to policy_evaluations |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_agent_id)` | FK to agents |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_merchant_id)` | FK to merchants |
| `product_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_product_id)` | FK to products |
| `offer_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_offer_id)` | FK to offers |
| `purchase_intent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_purchase_intent_id)` | FK to purchase_intents |
| `purchase_plan_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_purchase_plan_id)` | FK to purchase_plans |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_xai_explanations_commerce_transaction_id)` | FK to commerce_transactions |
| `explanation_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_xai_explanations_tenant_id_explanation_reference)` | Tenant-scoped explanation reference |
| `explanation_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (explanation_type IN ('shap', 'feature_importance', 'counterfactual', 'local', 'global', 'hybrid', 'custom'))`, `INDEX (ix_xai_explanations_explanation_type)` | Explanation type |
| `explanation_status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'completed'`, `CHECK (explanation_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled'))`, `INDEX (ix_xai_explanations_explanation_status)` | Explanation status |
| `model_reference` | `VARCHAR(100)` | `NOT NULL` | `INDEX (ix_xai_explanations_model_reference)` | Model reference string |
| `model_version` | `VARCHAR(50)` | `NOT NULL` | — | Model version string |
| `explainer_type` | `VARCHAR(50)` | `NOT NULL` | `CHECK (explainer_type IN ('tree_shap', 'kernel_shap', 'linear_shap', 'deep_shap', 'generic_feature_importance', 'custom'))` | Explainer algorithm type |
| `base_value` | `NUMERIC(18,8)` | `NULLABLE` | — | Model base/expected output value |
| `prediction_value` | `NUMERIC(18,8)` | `NULLABLE` | — | Model prediction output value |
| `top_feature_count` | `INTEGER` | `NOT NULL` | `DEFAULT 0`, `CHECK (top_feature_count >= 0)` | Top feature count |
| `feature_importance` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret feature importance map |
| `shap_values` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret SHAP values map |
| `feature_snapshot` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret feature values map |
| `explanation_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret context payload |
| `explanation_metadata` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret metadata payload |
| `summary` | `VARCHAR(255)` | `NULLABLE` | — | High-level summary string |
| `reasoning_summary` | `TEXT` | `NULLABLE` | — | Human-readable explanation narrative |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_xai_explanations_request_id)` | Correlation request ID |
| `actor_type` | `VARCHAR(100)` | `NULLABLE` | — | Actor type |
| `actor_id` | `UUID` | `NULLABLE` | — | Actor UUID |
| `generated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_xai_explanations_generated_at)` | Timestamp generated |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | `NULLABLE` | — | Soft-delete timestamp |

---

## 2. Integrity & Security Controls

- **Tenant Isolation**: Every `XAIExplanation` belongs to exactly one tenant.
- **Foreign Keys**: 11 optional foreign keys using `ON DELETE RESTRICT`.
- **Signed Numerical Values**: `base_value` and `prediction_value` use signed `NUMERIC(18,8)` Decimal semantics. SHAP values in JSONB may be positive or negative.
- **Zero Secrets**: Plaintext passwords, tokens, API keys, card numbers, or private keys MUST NOT be stored in JSONB payloads or exposed in `__repr__`.
