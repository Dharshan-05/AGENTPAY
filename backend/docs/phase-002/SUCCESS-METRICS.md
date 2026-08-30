# AGENTPAY — Success Metrics Baseline

## 1. Overview

This document formalizes measurable product and engineering success metrics for AGENTPAY. Metrics are strictly classified into `TARGET`, `MEASURED`, and `NOT YET MEASURED` to prevent non-verifiable or fabricated benchmark claims.

---

## 2. Product Success Metrics

| Category | Metric Description | Target Value | Current Status | Validation Method |
| :--- | :--- | :--- | :--- | :--- |
| **Policy Coverage** | % of agent intents evaluated by AGENTGUARD | $100\%$ | NOT YET MEASURED | Gateway audit log count comparison |
| **Risk Coverage** | % of intent requests scored by FRAUDGUARD | $100\%$ | NOT YET MEASURED | Risk evaluation log counter |
| **Explainability** | % of decisions accompanied by XAI text trace | $100\%$ | NOT YET MEASURED | Audit record schema validation |
| **Auditability** | % of transactions logged in immutable store | $100\%$ | NOT YET MEASURED | DB append log verification |
| **Policy Enforcement**| Detection rate of un-policied agent payments | $100\%$ Blocked | NOT YET MEASURED | Automated penetration test suite |
| **Decision Latency** | End-to-end intent processing latency ($p_{99}$) | $\le 100\text{ ms}$ | NOT YET MEASURED | Apache JMeter / Locust benchmark |
| **Policy Engine Speed**| AGENTGUARD rule evaluation latency ($p_{99}$) | $\le 15\text{ ms}$ | NOT YET MEASURED | Server-side execution timer |
| **Risk Scoring Speed** | FRAUDGUARD feature calculation latency ($p_{99}$)| $\le 50\text{ ms}$ | NOT YET MEASURED | Server-side execution timer |
| **Emergency Stop** | Latency to pause all agents upon kill switch | $< 100\text{ ms}$ | NOT YET MEASURED | Redis cache purge latency timer |
| **False Positive Rate**| Rate of legitimate intents blocked by fraud model| $< 2.0\%$ | NOT YET MEASURED | Synthetic transaction bench test |

---

## 3. Metric Tracking Principles

1. **No Invented Numbers**: Metrics listed under `NOT YET MEASURED` remain unpopulated until benchmark tests execute in Phase 010+.
2. **Deterministic Baseline**: Target values represent non-negotiable SLA limits required for production-grade agentic commerce.
