# AGENTPAY + AGENTGUARD — Database & API Architecture Specification (Phase 009)

## Executive Summary

This directory contains the complete, production-grade **Database & API Architecture Specification** for **AGENTPAY** (Autonomous Payment Infrastructure), **AGENTGUARD** (Policy, Identity & Security Layer), and **FRAUDGUARD** (Explainable AI Risk Engine).

Designed for zero-trust autonomous agentic commerce, this architecture specifies the relational PostgreSQL database schemas, row-level security (RLS) multi-tenancy rules, double-entry financial accounting ledger engines, RESTful OpenAPI 3.0 contracts, transactional outbox event pipelines, and multi-tier API security controls.

---

## Document Index

| Section | Index | Document Title | Description |
| :--- | :--- | :--- | :--- |
| **DATABASE** | **01** | [`01-database-objectives.md`](01-database-objectives.md) | Database Core Objectives & Non-Negotiable Financial Invariants |
| | **02** | [`02-database-principles.md`](02-database-principles.md) | 20 Non-Negotiable Database Architectural Design Principles |
| | **03** | [`03-database-domain-boundaries.md`](03-database-domain-boundaries.md) | Logical Database Domain Boundaries & Table Ownership |
| | **04** | [`04-database-source-of-truth.md`](04-database-source-of-truth.md) | Authoritative Source of Truth, Derived Data & Cache Map |
| | **05** | [`05-entity-model.md`](05-entity-model.md) | Complete Relational Entity Model & Schema Inter-Relationships |
| | **06** | [`06-tenant-model.md`](06-tenant-model.md) | Multi-Tenant Data Hierarchy (`tenant_id` Cascading Scope) |
| | **07** | [`07-tenant-isolation.md`](07-tenant-isolation.md) | PostgreSQL Row-Level Security (RLS) Policy Specifications |
| | **08** | [`08-identifier-strategy.md`](08-identifier-strategy.md) | Identifier Strategy (UUID v4 / ULID vs Provider Identifiers) |
| | **09** | [`09-naming-conventions.md`](09-naming-conventions.md) | PostgreSQL Relational Database Naming Conventions (`snake_case`) |
| | **10** | [`10-timestamp-model.md`](10-timestamp-model.md) | Distributed Timestamp Architecture (`TIMESTAMPTZ` in UTC) |
| | **11** | [`11-money-model.md`](11-money-model.md) | Financial Precision Model (Integer Minor Units / `NUMERIC(18,4)`) |
| | **12** | [`12-currency-model.md`](12-currency-model.md) | ISO 4217 Currency Validation & Settlement Precision Rules |
| | **13** | [`13-order-schema.md`](13-order-schema.md) | `orders` Relational Table Schema & Constraint Definitions |
| | **14** | [`14-order-item-schema.md`](14-order-item-schema.md) | `order_items` Relational Table Schema & Line Total Constraints |
| | **15** | [`15-payment-schema.md`](15-payment-schema.md) | `payment_intents`, `payments`, `payment_attempts` Schemas |
| | **16** | [`16-payment-state-persistence.md`](16-payment-state-persistence.md) | 18-State Payment Machine Persistence & Optimistic Locking |
| | **17** | [`17-payment-authorization-schema.md`](17-payment-authorization-schema.md) | `payment_authorizations` Cryptographic Token Schema |
| | **18** | [`18-idempotency-schema.md`](18-idempotency-schema.md) | `idempotency_records` Table Schema & 24h Expiration Rules |
| | **19** | [`19-webhook-schema.md`](19-webhook-schema.md) | `webhook_events` Table Schema & Deduplication Constraints |
| | **20** | [`20-refund-schema.md`](20-refund-schema.md) | `refunds` & `refund_attempts` Table Schemas & Over-Refund Guard |
| | **21** | [`21-ledger-schema.md`](21-ledger-schema.md) | `ledger_accounts`, `ledger_transactions`, `ledger_entries` |
| | **22** | [`22-double-entry-schema.md`](22-double-entry-schema.md) | Double-Entry Accounting Engine Invariants ($\sum \text{Debit} = \sum \text{Credit}$) |
| | **23** | [`23-risk-schema.md`](23-risk-schema.md) | `risk_assessments` & `risk_decisions` Immutable Schemas |
| | **24** | [`24-trust-schema.md`](24-trust-schema.md) | `trust_assessments` & `trust_scores` Historical Schemas |
| | **25** | [`25-policy-schema.md`](25-policy-schema.md) | `policies`, `policy_versions`, `policy_rules` Schemas |
| | **26** | [`26-approval-schema.md`](26-approval-schema.md) | `approval_requests` Table Schema & 15m Expiration TTL |
| | **27** | [`27-agent-schema.md`](27-agent-schema.md) | `agents`, `agent_identities`, `agent_capabilities` Schemas |
| | **28** | [`28-secret-management.md`](28-secret-management.md) | Secret Storage Policy (HashiCorp Vault / Zero DB Secrets) |
| | **29** | [`29-audit-schema.md`](29-audit-schema.md) | `audit_events` Append-Only SHA-256 Block Chain Table Schema |
| | **30** | [`30-outbox-schema.md`](30-outbox-schema.md) | `outbox_events` Transactional Table Schema & Polling Index |
| | **31** | [`31-event-delivery-schema.md`](31-event-delivery-schema.md) | `event_deliveries` Table Schema & Idempotent Consumer State |
| | **32** | [`32-reconciliation-schema.md`](32-reconciliation-schema.md) | `reconciliation_records` & `reconciliation_items` Schemas |
| | **33** | [`33-index-strategy.md`](33-index-strategy.md) | Database Index Strategy (Partial, Composite, Cover Indexes) |
| | **34** | [`34-partitioning.md`](34-partitioning.md) | PostgreSQL Time-Based Declarative Table Partitioning Specs |
| | **35** | [`35-transactions.md`](35-transactions.md) | Atomic Database Transaction Boundaries & ACID Rules |
| | **36** | [`36-isolation-levels.md`](36-isolation-levels.md) | Transaction Isolation Levels (`READ COMMITTED` vs `SERIALIZABLE`)|
| | **37** | [`37-concurrency.md`](37-concurrency.md) | Pessimistic DB Row Locking (`SELECT FOR UPDATE`) & Optimistic Locking |
| | **38** | [`38-deadlock-strategy.md`](38-deadlock-strategy.md) | Database Lock Ordering, Deadlock Detection & Retry Strategy |
| | **39** | [`39-migrations.md`](39-migrations.md) | Database Migration Governance, Versioning & Rollback Rules |
| | **40** | [`40-zero-downtime-migrations.md`](40-zero-downtime-migrations.md) | Zero-Downtime Expand/Contract Database Migration Pattern |
| | **41** | [`41-backups.md`](41-backups.md) | Automated Database Backup Strategy (Full + Continuous WAL) |
| | **42** | [`42-disaster-recovery.md`](42-disaster-recovery.md) | Database RPO (< 1s) & RTO (< 15m) Point-in-Time Recovery |
| | **43** | [`43-database-security.md`](43-database-security.md) | Database Security & Connection Role Privilege Restrictions |
| | **44** | [`44-cache-architecture.md`](44-cache-architecture.md) | Redis Derived Data Caching, TTL & Cache Invalidation Rules |
| | **45** | [`45-data-retention.md`](45-data-retention.md) | Financial Data Retention, Archival & Legal Compliance Rules |
| | **46** | [`46-data-classification.md`](46-data-classification.md) | 5-Tier Data Classification & Sensitivity Handling Rules |
| | **47** | [`47-database-quality-gate.md`](47-database-quality-gate.md) | Pre-Deployment Database Quality Gate & Audit Scorecard |
| **API** | **48** | [`48-api-objectives.md`](48-api-objectives.md) | API Core Architectural Objectives & Safety Rules |
| | **49** | [`49-api-principles.md`](49-api-principles.md) | 20 Non-Negotiable REST API Design Principles |
| | **50** | [`50-api-versioning.md`](50-api-versioning.md) | REST API URI Path Versioning (`/api/v1/...`) Strategy |
| | **51** | [`51-resource-design.md`](51-resource-design.md) | RESTful Resource-Oriented Naming & Path Architecture |
| | **52** | [`52-authentication.md`](52-authentication.md) | Multi-Actor API Authentication (JWT, mTLS, HMAC Key Pairs) |
| | **53** | [`53-authorization.md`](53-authorization.md) | Multi-Tier Authorization (RBAC + ABAC + Agent Scopes) |
| | **54** | [`54-tenant-context.md`](54-tenant-context.md) | Trusted Server-Side Tenant Context Resolution |
| | **55** | [`55-agent-api.md`](55-agent-api.md) | Autonomous Agent Management REST Endpoints Specification |
| | **56** | [`56-agentguard-api.md`](56-agentguard-api.md) | AGENTGUARD Security Control Plane API Contracts |
| | **57** | [`57-policy-api.md`](57-policy-api.md) | Policy Engine & Policy Versioning REST Endpoints |
| | **58** | [`58-risk-api.md`](58-risk-api.md) | FRAUDGUARD ML Risk Evaluation API Specification |
| | **59** | [`59-trust-api.md`](59-trust-api.md) | Agent Trust Score Evaluation REST API Endpoints |
| | **60** | [`60-order-api.md`](60-order-api.md) | Order Management REST API Endpoints Specification |
| | **61** | [`61-payment-intent-api.md`](61-payment-intent-api.md) | Payment Intent Proposal REST API Contract Specs |
| | **62** | [`62-payment-api.md`](62-payment-api.md) | Core Payment Execution REST API Endpoints Specification |
| | **63** | [`63-refund-api.md`](63-refund-api.md) | Refund Execution & Query REST API Contracts |
| | **64** | [`64-approval-api.md`](64-approval-api.md) | Approval Center Escalation REST API Specification |
| | **65** | [`65-webhook-api.md`](65-webhook-api.md) | Ingress Razorpay Webhook Callback API Endpoint Specs |
| | **66** | [`66-reconciliation-api.md`](66-reconciliation-api.md) | Reconciliation Management & Discrepancy API Specs |
| | **67** | [`67-audit-api.md`](67-audit-api.md) | Read-Only Audit Log Search REST API Contracts |
| | **68** | [`68-idempotency-api.md`](68-idempotency-api.md) | Ingress API Endpoint Idempotency Header Execution Rules |
| | **69** | [`69-validation.md`](69-validation.md) | Strict Input Request Validation (Zod / JSON Schema) |
| | **70** | [`70-error-model.md`](70-error-model.md) | Standardized API Error Response Model Specification |
| | **71** | [`71-pagination.md`](71-pagination.md) | Cursor-Based Opaque Pagination Specification |
| | **72** | [`72-filtering.md`](72-filtering.md) | Safe Whitelisted Query Parameter Filtering Specification |
| | **73** | [`73-sorting.md`](73-sorting.md) | Whitelisted Deterministic Multi-Column Sort Architecture |
| | **74** | [`74-rate-limiting.md`](74-rate-limiting.md) | Redis Sliding-Window Multi-Tier Rate Limiting Engine |
| | **75** | [`75-api-security.md`](75-api-security.md) | Multi-Layer API Gateway Security Controls |
| | **76** | [`76-request-signing.md`](76-request-signing.md) | Agent Request HMAC-SHA256 Cryptographic Signature Specs |
| | **77** | [`77-observability.md`](77-observability.md) | OpenTelemetry Distributed W3C API Tracing Specs |
| | **78** | [`78-api-audit.md`](78-api-audit.md) | Automated API Mutation Security Audit Logging |
| | **79** | [`79-events.md`](79-events.md) | Standardized Domain Event Schema Architecture |
| | **80** | [`80-outbox.md`](80-outbox.md) | Transactional Outbox Pattern API Dispatch Integration |
| | **81** | [`81-transaction-matrix.md`](81-transaction-matrix.md) | Master API Endpoint to DB Transaction Execution Matrix |
| | **82** | [`82-cache-api.md`](82-cache-api.md) | Redis API Read Caching & Invalidation Strategy |
| | **83** | [`83-openapi.md`](83-openapi.md) | Complete OpenAPI 3.0 Contract Specification |
| | **84** | [`84-contract-governance.md`](84-contract-governance.md) | API Contract Governance & Deprecation Policy |
| | **85** | [`85-api-security-testing.md`](85-api-security-testing.md) | Automated API Security & Injection Penetration Suite |
| | **86** | [`86-api-quality-gate.md`](86-api-quality-gate.md) | Pre-Deployment API Quality Gate & Scorecard Report |
| **CROSS-CUTTING** | **87** | [`87-database-api-traceability.md`](87-database-api-traceability.md) | Complete API Endpoint to DB Schema Traceability Matrix |
| | **88** | [`88-payment-traceability.md`](88-payment-traceability.md) | End-to-End Payment Intent Flow Traceability Chain |
| | **89** | [`89-failure-matrix.md`](89-failure-matrix.md) | Master API & Database System Failure Recovery Matrix |
| | **90** | [`90-performance-architecture.md`](90-performance-architecture.md) | Target Sub-100ms API Latency & Query Budget SLA |
| | **91** | [`91-scalability.md`](91-scalability.md) | Database Write Scaling & Horizontal API Scaling Specs |
| | **92** | [`92-async-processing.md`](92-async-processing.md) | Asynchronous Background Task Execution Architecture |
| | **93** | [`93-job-architecture.md`](93-job-architecture.md) | Idempotent Background Cron Job Worker Architecture |
| | **94** | [`94-disaster-recovery.md`](94-disaster-recovery.md) | Cross-Cutting Disaster Recovery & Backup Plan |
| | **95** | [`95-security-red-team.md`](95-security-red-team.md) | 70 Combined Database & API Red-Team Attack Scenarios |
| | **96** | [`96-final-quality-gate.md`](96-final-quality-gate.md) | Phase 009 Final Master Quality Gate Audit Report |

---

## ADR Index (`adrs/`)

* **Database ADRs (`adrs/DB-ADR-001.md` to `adrs/DB-ADR-020.md`)**: 20 Database Architecture Decision Records.
* **API ADRs (`adrs/API-ADR-001.md` to `adrs/API-ADR-020.md`)**: 20 API Architecture Decision Records.

---

## Diagram Library (`diagrams/`)

* **Database Diagrams (`diagrams/db-001.mmd` to `diagrams/db-025.mmd`)**: 25 Relational Schema & Transaction Diagrams.
* **API Diagrams (`diagrams/api-001.mmd` to `diagrams/api-025.mmd`)**: 25 API Gateway & Endpoint Flow Diagrams.
