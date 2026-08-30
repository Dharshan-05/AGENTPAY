# AGENTPAY Security Events Schema Architecture (Phase 073)

## Executive Summary

This document formalizes the architectural specification and schema layout for `security_events` in **AGENTPAY** (`Phase 073`).

`security_events` provides a normalized, immutable security-event log dedicated to security-relevant activities across the AGENTPAY platform.

---

## 1. Schema Specifications (`security_events`)

| Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | `NOT NULL` | `PRIMARY KEY (pk_security_events)` | Canonical primary key (UUIDv7) |
| `tenant_id` | `UUID` | `NOT NULL` | `INDEX (ix_security_events_tenant_id)` | Multi-tenancy isolation key |
| `event_reference` | `VARCHAR(100)` | `NOT NULL` | `UNIQUE (uq_security_events_tenant_id_event_reference)`, `INDEX (ix_security_events_event_reference)` | Tenant-scoped event reference |
| `event_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'system'`, `CHECK (event_type IN ('authentication', 'authorization', 'policy', 'credential', 'tenant_isolation', 'suspicious_activity', 'security_control', 'attack', 'system'))`, `INDEX (ix_security_events_event_type)` | Event classification |
| `event_action` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'security_alert'`, `CHECK (event_action IN ('login', 'logout', 'authentication_failed', 'authorization_denied', 'permission_changed', 'credential_used', 'credential_failed', 'policy_blocked', 'policy_violation', 'tenant_boundary_violation', 'suspicious_request', 'attack_detected', 'security_control_triggered', 'security_alert', 'security_reviewed'))`, `INDEX (ix_security_events_event_action)` | Specific security action |
| `event_result` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'success'`, `CHECK (event_result IN ('success', 'failure', 'blocked', 'detected', 'review_required', 'error'))`, `INDEX (ix_security_events_event_result)` | Security event outcome |
| `severity` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'medium'`, `CHECK (severity IN ('low', 'medium', 'high', 'critical'))`, `INDEX (ix_security_events_severity)` | Severity assessment |
| `source` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'internal'`, `CHECK (source IN ('internal', 'external', 'agent', 'merchant', 'webhook', 'policy_engine', 'risk_engine', 'siem', 'system'))`, `INDEX (ix_security_events_source)` | Event origin source |
| `request_id` | `VARCHAR(100)` | `NULLABLE` | `INDEX (ix_security_events_request_id)` | Correlation request ID |
| `actor_type` | `VARCHAR(50)` | `NOT NULL` | `DEFAULT 'user'` | Actor type classification |
| `actor_id` | `UUID` | `NULLABLE` | `INDEX (ix_security_events_actor_id)` | Actor UUID |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | — | IP address context |
| `user_agent` | `VARCHAR(500)` | `NULLABLE` | — | User agent string |
| `user_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_user_id)` | User FK |
| `agent_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_agent_id)` | Agent FK |
| `merchant_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_merchant_id)` | Merchant FK |
| `security_violation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_security_violation_id)` | Security violation FK |
| `risk_signal_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_risk_signal_id)` | Risk signal FK |
| `policy_evaluation_id` | `UUID` | `NULLABLE` | `FOREIGN KEY ON DELETE RESTRICT`, `INDEX (ix_security_events_policy_evaluation_id)` | Policy evaluation FK |
| `event_payload` | `JSONB` | `NULLABLE` | `DEFAULT '{}'` | Non-secret event payload |
| `occurred_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()`, `INDEX (ix_security_events_occurred_at)` | Occurrence timestamp |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `DEFAULT NOW()` | Record creation timestamp |

---

## 2. Security Controls & Guidelines

- **Append-Only Immutability**: No `updated_at` or `deleted_at` columns exist. Records are immutable.
- **Zero Secrets Storage**: Passwords, API keys, card PAN, CVV, PIN, or tokens MUST NOT be stored in `event_payload` or exposed in `__repr__`.
- **Tenant Isolation**: Mandatory indexed `tenant_id` on all records.
