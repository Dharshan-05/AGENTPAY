# AGENTPAY

> **Autonomous Agentic Payment Infrastructure with Trusted Security, Policy Enforcement & Explainable AI Risk Control**

---

## 1. Overview

**AGENTPAY** is an intelligent transaction security, authorization, and risk management platform designed for autonomous agentic commerce. As autonomous AI agents perform product discovery, supplier negotiation, and transaction initiation on behalf of users, AGENTPAY provides the critical trust layer that sits between AI agents and financial payment execution.

---

## 2. Core Pillars

```
+-----------------------------------------------------------------------+
|                                 USER                                  |
+-----------------------------------------------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                               AI AGENT                                |
+-----------------------------------------------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                            AGENTPAY ENGINE                            |
|                                                                       |
|   +-----------------------+                 +-----------------------+ |
|   |      AGENTGUARD       |                 |      FRAUDGUARD       | |
|   | Policy & Identity     | <-------------> | Risk & Anomaly Engine | |
|   +-----------------------+                 +-----------------------+ |
|                                                                       |
|                       +-----------------------+                       |
|                       |    XAI EXPLANATION    |                       |
|                       +-----------------------+                       |
+-----------------------------------------------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                           PAYMENT EXECUTION                           |
+-----------------------------------------------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                         IMMUTABLE AUDIT TRAIL                         |
+-----------------------------------------------------------------------+
```

### AGENTGUARD — Policy & Security Layer
Determines whether an AI AGENT is authorized to perform a financial action based on cryptographically verified agent identity, spending limits, category restrictions, merchant controls, and operating windows.

### FRAUDGUARD — Explainable Risk & Anomaly Engine
Evaluates real-time behavioral anomaly signals, transaction velocity, merchant trust, and historical patterns to generate normalized risk scores and fraud probabilities.

### XAI Engine — Transparent Decision Rationale
Translates risk scores and feature contributions into human-understandable explanations answering **WHY** a transaction was approved, challenged, or blocked.

---

## 3. The 15-Step Payment Trust Pipeline

1. **Intent Creation**: AI Agent submits structured `PAYMENT INTENT`.
2. **Agent Authentication**: Verify HMAC signature & cryptographic credentials.
3. **Agent Permission Check**: Validate agent status (`ACTIVE`) and permissions.
4. **User Auth Check**: Validate owner account state and Emergency Stop status.
5. **Parameter Validation**: Validate request schema, currency, and amount.
6. **AGENTGUARD Evaluation**: Evaluate static policy rules and category boundaries.
7. **FRAUDGUARD Signal Extraction**: Calculate 12-dimensional risk features.
8. **Risk Calculation**: Generate normalized `RISK SCORE` (0 - 100).
9. **XAI Explanation**: Generate feature attributions and natural language rationale.
10. **Authorization Decision**: Output `ALLOW`, `REVIEW`, `CHALLENGE`, or `BLOCK`.
11. **Human Approval Escalation**: Route `REVIEW` decisions to Approval Center.
12. **Payment Execution**: Dispatch authorized intent to payment processor adapter.
13. **Result Verification**: Verify settlement response from gateway.
14. **Continuous Monitoring**: Post-execution anomaly tracking.
15. **Immutable Audit Logging**: Write complete decision trace to append-only log store.

---

## 4. Documentation Sitemap (Phase 001)

The complete product vision, scope, and engineering specifications are documented under `docs/phase-001/`:

* [`PRODUCT-VISION.md`](docs/phase-001/PRODUCT-VISION.md) — Problem statement, product vision, and strategic pillars.
* [`PRODUCT-SCOPE.md`](docs/phase-001/PRODUCT-SCOPE.md) — System scope, component responsibilities, and system boundaries.
* [`PRODUCT-PILLARS.md`](docs/phase-001/PRODUCT-PILLARS.md) — Deep dive into Agent Identity, User Authorization, and AGENTGUARD.
* [`USERS-AND-ACTORS.md`](docs/phase-001/USERS-AND-ACTORS.md) — Detailed taxonomy of system actors, responsibilities, and permissions.
* [`MVP-SCOPE.md`](docs/phase-001/MVP-SCOPE.md) — Must-have features, boundaries, and hackathon scope constraints.
* [`OUT-OF-SCOPE.md`](docs/phase-001/OUT-OF-SCOPE.md) — Explicit MVP deferrals and future v1.5 / v2.0 roadmap.
* [`USER-JOURNEYS.md`](docs/phase-001/USER-JOURNEYS.md) — End-to-end user journeys for primary operational scenarios.
* [`AGENT-LIFECYCLE.md`](docs/phase-001/AGENT-LIFECYCLE.md) — Agent state machine, HMAC signatures, and key rotation.
* [`PAYMENT-LIFECYCLE.md`](docs/phase-001/PAYMENT-LIFECYCLE.md) — 15-step payment trust pipeline and idempotency rules.
* [`TRUST-MODEL.md`](docs/phase-001/TRUST-MODEL.md) — Multi-layer agent trust score formula, factors, and trust tiers.
* [`RISK-DECISION-MODEL.md`](docs/phase-001/RISK-DECISION-MODEL.md) — FraudGuard risk dimensions, JSON output schema, and decision matrix.
* [`SAFETY-PRINCIPLES.md`](docs/phase-001/SAFETY-PRINCIPLES.md) — 12 Non-negotiable safety principles for agentic financial systems.
* [`HACKATHON-DEMO.md`](docs/phase-001/HACKATHON-DEMO.md) — 3-minute live hackathon demo script and transaction scenarios.
* [`PHASE-001-COMPLETION.md`](docs/phase-001/PHASE-001-COMPLETION.md) — Phase 001 completion report and validation summary.

---

## 5. Security & Safety Principles

1. **Authentication ≠ Trust**: Key validity proves identity, not transaction safety.
2. **Deterministic Authority**: Financial authorization is governed by policy rules and verified risk thresholds, not raw LLM outputs.
3. **Universal Explainability**: Every authorization decision produces human-readable explanations.
4. **Instant Revocability**: Human owners can pause, revoke, or emergency-stop agents at any time.
5. **Zero Credential Exposure**: Raw banking credentials or payment secrets are never exposed to AI agents or LLM contexts.
