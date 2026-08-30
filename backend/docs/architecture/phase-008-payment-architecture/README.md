# AGENTPAY + AGENTGUARD — Payment Architecture Specification (Phase 008)

## Executive Summary

This directory contains the authoritative, production-grade **Payment Architecture Specification** for **AGENTPAY** (Autonomous Payment Infrastructure), **AGENTGUARD** (Policy, Identity & Security Gate), and **FRAUDGUARD** (Explainable AI Risk Engine).

Designed for zero-trust autonomous agentic commerce, this architecture specifies end-to-end payment intent lifecycle processing, payment authorization contexts, abstract provider adapter boundaries, Razorpay gateway integration, 18-state payment transaction machines, double-entry financial ledger accounting, webhook reconciliation, and emergency kill switches.

---

## Document Index

| Index | Document Title | Description |
| :--- | :--- | :--- |
| **01** | [`01-payment-objectives.md`](01-payment-objectives.md) | Core Payment System Objectives & Boundary Rules |
| **02** | [`02-payment-principles.md`](02-payment-principles.md) | 30 Non-Negotiable Payment Design Principles |
| **03** | [`03-payment-domain-model.md`](03-payment-domain-model.md) | Payment Domain Model Entities & Tenant Ownership |
| **04** | [`04-payment-identifiers.md`](04-payment-identifiers.md) | 18 Distinct GUID Identifiers & Provider Mappings |
| **05** | [`05-payment-system-architecture.md`](05-payment-system-architecture.md) | End-to-End Logical Payment Processing Architecture |
| **06** | [`06-payment-orchestrator.md`](06-payment-orchestrator.md) | Payment Orchestrator Component Specifications |
| **07** | [`07-provider-abstraction.md`](07-provider-abstraction.md) | Abstract `IPaymentProvider` & Adapter Pattern Interface |
| **08** | [`08-razorpay-integration.md`](08-razorpay-integration.md) | Razorpay API Gateway Adapter Specifications |
| **09** | [`09-payment-intent.md`](09-payment-intent.md) | `PaymentIntent` Schema, Lifecycle & State Rules |
| **10** | [`10-payment-authorization.md`](10-payment-authorization.md) | Cryptographic `PaymentAuthorizationContext` Specs |
| **11** | [`11-payment-state-machine.md`](11-payment-state-machine.md) | 18-State Payment Transaction State Machine |
| **12** | [`12-state-transition-ownership.md`](12-state-transition-ownership.md) | State Transition Authority & Execution Rights Matrix |
| **13** | [`13-idempotency.md`](13-idempotency.md) | Multi-Tier Redis 24-Hour Idempotency Locking |
| **14** | [`14-duplicate-prevention.md`](14-duplicate-prevention.md) | Multi-Level Double-Spend & Duplicate Execution Defenses |
| **15** | [`15-concurrency-control.md`](15-concurrency-control.md) | Pessimistic DB Row Locking (`SELECT FOR UPDATE`) |
| **16** | [`16-money-precision.md`](16-money-precision.md) | Financial Precision (PostgreSQL `NUMERIC` / Minor Units) |
| **17** | [`17-currency-architecture.md`](17-currency-architecture.md) | Currency Architecture, Validation & Multi-Currency Rules |
| **18** | [`18-order-payment-separation.md`](18-order-payment-separation.md) | Structural Decoupling of Orders vs Payment Settlements |
| **19** | [`19-payment-attempts.md`](19-payment-attempts.md) | `PaymentAttempt` Entity Tracking & Retry Eligibility |
| **20** | [`20-retry-architecture.md`](20-retry-architecture.md) | State-Aware Exponential Backoff & Jitter Retry Engine |
| **21** | [`21-timeout-handling.md`](21-timeout-handling.md) | Provider Gateway Timeout SLA (5,000ms Hard Cap) |
| **22** | [`22-unknown-payment-state.md`](22-unknown-payment-state.md) | `PAYMENT_STATUS_UNKNOWN` Verification Protocol |
| **23** | [`23-webhook-architecture.md`](23-webhook-architecture.md) | Async Webhook Listener & Signature Verification Engine |
| **24** | [`24-webhook-replay-protection.md`](24-webhook-replay-protection.md) | Webhook Event Deduplication & Replay Prevention |
| **25** | [`25-webhook-source-security.md`](25-webhook-source-security.md) | Webhook HMAC-SHA256 Signature Verification Rules |
| **26** | [`26-refund-architecture.md`](26-refund-architecture.md) | Full & Partial Refund Execution Architecture |
| **27** | [`27-refund-authorization.md`](27-refund-authorization.md) | Refund Capability Authorization & Policy Checks |
| **28** | [`28-refund-state-machine.md`](28-refund-state-machine.md) | 8-State Refund Lifecycle State Machine |
| **29** | [`29-partial-refunds.md`](29-partial-refunds.md) | Cumulative Refund Amount Tracking & Over-Refund Guard |
| **30** | [`30-financial-ledger.md`](30-financial-ledger.md) | Immutable Financial Ledger & Accounting Records |
| **31** | [`31-double-entry.md`](31-double-entry.md) | Double-Entry Accounting Engine ($\sum \text{Debit} = \sum \text{Credit}$) |
| **32** | [`32-balance-management.md`](32-balance-management.md) | Available vs Pending vs Reserved Balance Controls |
| **33** | [`33-reconciliation.md`](33-reconciliation.md) | Internal vs Razorpay Gateway Settlement Reconciliation |
| **34** | [`34-reconciliation-states.md`](34-reconciliation-states.md) | 9 Reconciliation Discrepancy Classifications |
| **35** | [`35-reconciliation-schedule.md`](35-reconciliation-schedule.md) | Real-Time Webhook + Nightly Batch Reconciliation Jobs |
| **36** | [`36-financial-integrity.md`](36-financial-integrity.md) | 8 Invariant Financial Integrity Rules |
| **37** | [`37-payment-security.md`](37-payment-security.md) | Phase 006 Security Controls Integration |
| **38** | [`38-agent-payment-flow.md`](38-agent-payment-flow.md) | End-to-End Autonomous Agent Payment Step Execution |
| **39** | [`39-human-approval.md`](39-human-approval.md) | Escalation Approval Cards & 15-Minute Expiration TTL |
| **40** | [`40-payment-policy.md`](40-payment-policy.md) | Multi-Dimensional Payment Policy Cap Configuration |
| **41** | [`41-payment-risk.md`](41-payment-risk.md) | FRAUDGUARD ML Risk Score Integration |
| **42** | [`42-risk-payment-separation.md`](42-risk-payment-separation.md) | Structural Decoupling of Risk, Policy & Authorization |
| **43** | [`43-payment-error-model.md`](43-payment-error-model.md) | 13 Normalized Internal Payment Error Categories |
| **44** | [`44-payment-events.md`](44-payment-events.md) | 18 Domain Event Schemas (`PaymentAuthorized`, etc.) |
| **45** | [`45-event-ordering.md`](45-event-ordering.md) | Sequence Numbers & Out-of-Order Event Handling |
| **46** | [`46-outbox-pattern.md`](46-outbox-pattern.md) | Transactional Outbox Pattern for Atomic Event Dispatch |
| **47** | [`47-payment-notifications.md`](47-payment-notifications.md) | Verified Payment Status User Notifications |
| **48** | [`48-payment-audit.md`](48-payment-audit.md) | SHA-256 Append-Only Audit Logging Chain |
| **49** | [`49-payment-observability.md`](49-payment-observability.md) | Distributed OpenTelemetry Tracing (`payment_id`) |
| **50** | [`50-payment-fraud-controls.md`](50-payment-fraud-controls.md) | Real-Time Fraud Prevention & Anomaly Detection |
| **51** | [`51-payment-kill-switch.md`](51-payment-kill-switch.md) | Multi-Tier Emergency Payment Kill Switch Architecture |
| **52** | [`52-payment-limits.md`](52-payment-limits.md) | Multi-Tier Spending Limit Counters in Redis |
| **53** | [`53-provider-failure.md`](53-provider-failure.md) | Provider Outage & Circuit Breaker Degradation Playbook |
| **54** | [`54-disaster-recovery.md`](54-disaster-recovery.md) | Financial RPO (< 1s) & RTO (< 15m) Recovery Protocol |
| **55** | [`55-data-consistency.md`](55-data-consistency.md) | Strong vs Eventual Data Consistency Model Assignment |
| **56** | [`56-multi-tenancy.md`](56-multi-tenancy.md) | PostgreSQL RLS Multi-Tenant Data Isolation |
| **57** | [`57-payment-api.md`](57-payment-api.md) | RESTful API Endpoints (`/api/v1/payments/...`) |
| **58** | [`58-api-idempotency.md`](58-api-idempotency.md) | Ingress API Endpoint Idempotency Matrix |
| **59** | [`59-database-constraints.md`](59-database-constraints.md) | Database Unique Constraints, Checks & Foreign Keys |
| **60** | [`60-payment-security-testing.md`](60-payment-security-testing.md) | Automated Payment Security & Double-Spend Test Suite |
| **61** | [`61-payment-red-team.md`](61-payment-red-team.md) | 35 Payment Red-Team Attack Simulation Scenarios |
| **62** | [`62-payment-diagrams.md`](62-payment-diagrams.md) | Index of 30 Payment System Diagrams (`diagrams/`) |
| **63** | [`63-payment-adrs.md`](63-payment-adrs.md) | Index of 20 Payment Architecture Decision Records (`adrs/`) |
| **64** | [`64-payment-quality-gate.md`](64-payment-quality-gate.md) | Pre-Deployment Payment Quality Gate & Audit Scorecard |

---

## Payment ADR Index (`adrs/`)

1. [`PAY-ADR-001.md`](adrs/PAY-ADR-001.md) — Payment Orchestrator
2. [`PAY-ADR-002.md`](adrs/PAY-ADR-002.md) — Provider Abstraction
3. [`PAY-ADR-003.md`](adrs/PAY-ADR-003.md) — Razorpay Adapter
4. [`PAY-ADR-004.md`](adrs/PAY-ADR-004.md) — Payment Intent
5. [`PAY-ADR-005.md`](adrs/PAY-ADR-005.md) — Payment Authorization
6. [`PAY-ADR-006.md`](adrs/PAY-ADR-006.md) — Payment State Machine
7. [`PAY-ADR-007.md`](adrs/PAY-ADR-007.md) — Idempotency
8. [`PAY-ADR-008.md`](adrs/PAY-ADR-008.md) — Duplicate Prevention
9. [`PAY-ADR-009.md`](adrs/PAY-ADR-009.md) — Concurrency Control
10. [`PAY-ADR-010.md`](adrs/PAY-ADR-010.md) — Money Precision
11. [`PAY-ADR-011.md`](adrs/PAY-ADR-011.md) — Currency Handling
12. [`PAY-ADR-012.md`](adrs/PAY-ADR-012.md) — Webhook Security
13. [`PAY-ADR-013.md`](adrs/PAY-ADR-013.md) — Refund Architecture
14. [`PAY-ADR-014.md`](adrs/PAY-ADR-014.md) — Financial Ledger
15. [`PAY-ADR-015.md`](adrs/PAY-ADR-015.md) — Reconciliation
16. [`PAY-ADR-016.md`](adrs/PAY-ADR-016.md) — Event Outbox
17. [`PAY-ADR-017.md`](adrs/PAY-ADR-017.md) — Payment Risk
18. [`PAY-ADR-018.md`](adrs/PAY-ADR-018.md) — Human Approval
19. [`PAY-ADR-019.md`](adrs/PAY-ADR-019.md) — Payment Kill Switch
20. [`PAY-ADR-020.md`](adrs/PAY-ADR-020.md) — Provider Failure Recovery

---

## Payment Diagrams Library (`diagrams/`)

1. [`01-payment-system-context.mmd`](diagrams/01-payment-system-context.mmd)
2. [`02-payment-high-level-architecture.mmd`](diagrams/02-payment-high-level-architecture.mmd)
3. [`03-payment-domain-model.mmd`](diagrams/03-payment-domain-model.mmd)
4. [`04-payment-orchestrator.mmd`](diagrams/04-payment-orchestrator.mmd)
5. [`05-provider-abstraction.mmd`](diagrams/05-provider-abstraction.mmd)
6. [`06-razorpay-integration.mmd`](diagrams/06-razorpay-integration.mmd)
7. [`07-payment-intent-lifecycle.mmd`](diagrams/07-payment-intent-lifecycle.mmd)
8. [`08-payment-authorization.mmd`](diagrams/08-payment-authorization.mmd)
9. [`09-payment-state-machine.mmd`](diagrams/09-payment-state-machine.mmd)
10. [`10-payment-attempt-flow.mmd`](diagrams/10-payment-attempt-flow.mmd)
11. [`11-idempotency-architecture.mmd`](diagrams/11-idempotency-architecture.mmd)
12. [`12-duplicate-prevention.mmd`](diagrams/12-duplicate-prevention.mmd)
13. [`13-concurrency-control.mmd`](diagrams/13-concurrency-control.mmd)
14. [`14-unknown-payment-state.mmd`](diagrams/14-unknown-payment-state.mmd)
15. [`15-webhook-security.mmd`](diagrams/15-webhook-security.mmd)
16. [`16-webhook-processing.mmd`](diagrams/16-webhook-processing.mmd)
17. [`17-refund-architecture.mmd`](diagrams/17-refund-architecture.mmd)
18. [`18-refund-state-machine.mmd`](diagrams/18-refund-state-machine.mmd)
19. [`19-ledger-architecture.mmd`](diagrams/19-ledger-architecture.mmd)
20. [`20-double-entry-ledger.mmd`](diagrams/20-double-entry-ledger.mmd)
21. [`21-reconciliation-architecture.mmd`](diagrams/21-reconciliation-architecture.mmd)
22. [`22-payment-event-architecture.mmd`](diagrams/22-payment-event-architecture.mmd)
23. [`23-outbox-pattern.mmd`](diagrams/23-outbox-pattern.mmd)
24. [`24-human-approval-payment-flow.mmd`](diagrams/24-human-approval-payment-flow.mmd)
25. [`25-agent-payment-flow.mmd`](diagrams/25-agent-payment-flow.mmd)
26. [`26-payment-risk-architecture.mmd`](diagrams/26-payment-risk-architecture.mmd)
27. [`27-payment-kill-switch.mmd`](diagrams/27-payment-kill-switch.mmd)
28. [`28-payment-failure-recovery.mmd`](diagrams/28-payment-failure-recovery.mmd)
29. [`29-payment-observability.mmd`](diagrams/29-payment-observability.mmd)
30. [`30-payment-red-team-threat-model.mmd`](diagrams/30-payment-red-team-threat-model.mmd)
