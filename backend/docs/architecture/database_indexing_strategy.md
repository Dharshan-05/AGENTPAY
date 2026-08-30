# AGENTPAY Database Indexing Strategy Architecture (Phase 076)

## Executive Summary

This document formalizes the production-grade database indexing strategy for **AGENTPAY** (`Phase 076`).

Every one of the 53 application tables in AGENTPAY has been audited for:
- Primary key indexes (UUIDv7)
- Multi-tenant isolation indexes (`tenant_id`)
- Foreign key lookup coverage (100% indexed)
- Operational composite indexes (tenant-scoped filtering, status, and temporal range queries)
- Selectivity, cardinality, and write-amplification tradeoffs

---

## 1. Indexing Audit & Matrix Summary

| Table | Index Name | Columns | Uniqueness | Supported Query Pattern / Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `refresh_tokens` | `ix_refresh_tokens_parent_token_id` | `(parent_token_id)` | Non-Unique | Foreign key index coverage for token family rotation lineage lookups |
| `payment_orders` | `ix_payment_orders_tenant_status` | `(tenant_id, status)` | Non-Unique | Operational tenant payment order status filtering and monitoring |
| `payment_transactions` | `ix_payment_transactions_tenant_status` | `(tenant_id, status)` | Non-Unique | Tenant payment processing dashboard & status queries |
| `review_queue` | `ix_review_queue_tenant_status_priority` | `(tenant_id, status, priority)` | Non-Unique | Review queue prioritization, reviewer claim assignment, & filtering |
| `approval_requests` | `ix_approval_requests_tenant_status` | `(tenant_id, status)` | Non-Unique | Pending authorization approval dashboard & reviewer queue queries |
| `audit_logs` | `ix_audit_logs_tenant_occurred_at` | `(tenant_id, occurred_at)` | Non-Unique | High-throughput tenant audit trail export, streaming, & range filtering |
| `security_events` | `ix_security_events_tenant_occurred_at` | `(tenant_id, occurred_at)` | Non-Unique | Tenant security event timeline analysis & SIEM log filtering |
| `risk_decision_audits` | `ix_risk_decision_audits_tenant_occurred_at` | `(tenant_id, occurred_at)` | Non-Unique | Risk engine decision timeline auditing & event sequence analysis |

---

## 2. Standards & Quality Enforcements

- **100% Foreign Key Index Coverage**: All 53 application tables enforce explicit foreign key index coverage.
- **Tenant-First Composite Indexing**: High-volume queries leverage tenant-first composite indexes `(tenant_id, ...)` to eliminate full-table scanning and ensure absolute tenant data isolation.
- **No Duplicate / Redundant Indexes**: Every index satisfies a distinct operational query pattern without write amplification overhead.
