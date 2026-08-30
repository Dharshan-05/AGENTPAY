# AGENTPAY Risk Decision Audits Schema Architecture (Phase 075)

## Executive Summary

This document formalizes the architectural specification and schema layout for `risk_decision_audits` in **AGENTPAY** (`Phase 075`).

`risk_decision_audits` records the complete audit trail surrounding risk-engine decisions, capturing how and why decisions were reached.

---

## 1. Schema Specifications (`risk_decision_audits`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_risk_decision_audits)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_risk_decision_audits_tenant_id)` | Multi-tenancy isolation key |
| `decision_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_risk_decision_audits_tenant_id_decision_reference)`, `INDEX (ix_risk_decision_audits_decision_reference)` | Tenant-scoped decision reference |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_risk_decision_audits_request_id)` | Correlation request ID |
| `decision_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'transaction'`, `CHECK (decision_type IN ('authorization', 'transaction', 'fraud', 'risk', 'payment', 'commerce', 'spending', 'agent', 'security'))`, `INDEX (ix_risk_decision_audits_decision_type)` | Decision scope |
| `decision` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'allow'`, `CHECK (decision IN ('allow', 'deny', 'challenge', 'review', 'block', 'require_approval'))`, `INDEX (ix_risk_decision_audits_decision)` | Evaluated decision action |
| `result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'`, `CHECK (result IN ('success', 'failure', 'error', 'skipped'))`, `INDEX (ix_risk_decision_audits_result)` | Decision result outcome |
| `decision_source` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'risk_engine'`, `INDEX (ix_risk_decision_audits_decision_source)` | Source subsystem |
| `risk_score` | `NUMERIC(8,4)` | `NOT NULL` | `CHECK (risk_score >= 0 AND risk_score <= 100)` | Numerical risk score |
| `confidence_score` | `NUMERIC(8,4)` | `NOT NULL` | `CHECK (confidence_score >= 0 AND confidence_score <= 1)` | Numerical confidence score |
| `model_name` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_risk_decision_audits_model_name)` | Traceable risk model name |
| `model_version` | `VARCHAR(50)` | `NULLABLE` | — | Traceable model version |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_policy_evaluation_id)` | Policy evaluation FK |
| `security_policy_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_security_policy_id)` | Security policy FK |
| `policy_rule_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_policy_rule_id)` | Policy rule FK |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_risk_signal_id)` | Risk signal FK |
| `fraud_prediction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_fraud_prediction_id)` | Fraud prediction FK |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_security_violation_id)` | Security violation FK |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_agent_id)` | Agent FK |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_merchant_id)` | Merchant FK |
| `commerce_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_commerce_transaction_id)` | Commerce transaction FK |
| `payment_transaction_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_risk_decision_audits_payment_transaction_id)` | Payment transaction FK |
| `decision_reason` | `VARCHAR(500)` | `NULLABLE` | — | Decision rationale summary |
| `decision_context` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret decision metadata |
| `input_summary` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Sanitized input feature summary |
| `output_summary` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Sanitized output decision breakdown |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_risk_decision_audits_occurred_at)` | Occurrence timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Security Controls & Guidelines

- **Append-Only Immutability**: No `updated_at` or `deleted_at` columns exist. Decisions preserve historical audit integrity.
- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in summaries or payloads, or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
