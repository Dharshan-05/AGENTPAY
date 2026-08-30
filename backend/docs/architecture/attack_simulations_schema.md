# AGENTPAY Attack Simulations Schema Architecture (Phase 074)

## Executive Summary

This document formalizes the architectural specification and schema layout for `attack_simulations` in **AGENTPAY** (`Phase 074`).

`attack_simulations` stores controlled security attack simulation / adversarial testing records used to evaluate AGENTPAY's security controls.

---

## 1. Schema Specifications (`attack_simulations`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_attack_simulations)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_attack_simulations_tenant_id)` | Multi-tenancy isolation key |
| `simulation_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_attack_simulations_tenant_id_simulation_reference)`, `INDEX (ix_attack_simulations_simulation_reference)` | Tenant-scoped simulation reference |
| `simulation_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'policy_bypass'`, `CHECK (simulation_type IN ('authentication_bypass', 'authorization_bypass', 'tenant_isolation', 'policy_bypass', 'fraud_detection', 'risk_manipulation', 'replay', 'webhook_abuse', 'rate_limit', 'credential_abuse', 'payment_abuse'))`, `INDEX (ix_attack_simulations_simulation_type)` | Simulation type classification |
| `scenario` | `VARCHAR(200)` | `NOT NULL` | — | Test scenario description |
| `status` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'planned'`, `CHECK (status IN ('planned', 'queued', 'running', 'completed', 'failed', 'cancelled'))`, `INDEX (ix_attack_simulations_status)` | Simulation lifecycle status |
| `severity` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'medium'`, `CHECK (severity IN ('low', 'medium', 'high', 'critical'))`, `INDEX (ix_attack_simulations_severity)` | Severity score |
| `outcome` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'blocked'`, `CHECK (outcome IN ('passed', 'failed', 'blocked', 'detected', 'undetected', 'inconclusive'))`, `INDEX (ix_attack_simulations_outcome)` | Test result outcome |
| `target_component` | `VARCHAR(100)` | `NOT NULL` | — | Target subsystem under test |
| `target_resource_type` | `VARCHAR(100)` | `NULLABLE` | — | Optional target entity type |
| `target_resource_id` | `UUID` | `NULLABLE` | `INDEX (ix_attack_simulations_target_resource_id)` | Optional target UUID |
| `initiated_by` | `UUID` | `NOT NULL` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_attack_simulations_initiated_by)` | User UUID initiating simulation |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_attack_simulations_request_id)` | Correlation request ID |
| `simulation_parameters` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret safe test parameters |
| `expected_result` | `VARCHAR(50)` | `NOT NULL` | — | Expected test result |
| `actual_result` | `VARCHAR(50)` | `NULLABLE` | — | Observed test result |
| `findings` | `VARCHAR(1000)` | `NULLABLE` | — | Summary of findings |
| `evidence_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Safe evidence metadata |
| `risk_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100))` | Evaluated risk score |
| `confidence_score` | `NUMERIC(8,4)` | `NULLABLE` | `CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))` | Confidence metric |
| `started_at` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_attack_simulations_started_at)` | Simulation start timestamp |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` | `INDEX (ix_attack_simulations_completed_at)` | Simulation completion timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Security Controls & Guidelines

- **Append-Only Immutability**: No `updated_at` or `deleted_at` columns exist. Records preserve historical simulation audit history.
- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in parameters or evidence payloads, or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
