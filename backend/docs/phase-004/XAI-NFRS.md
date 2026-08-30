# AGENTPAY — XAI Non-Functional Requirements

## 1. Overview

XAI requirements define explanation latency SLAs, 100% trace completeness guarantees, and explanation correctness verification rules.

---

## 2. Requirement Baseline

### NFR-XAI-001: 100% Explanation Trace Completeness SLA
* **NFR ID**: `NFR-XAI-001`
* **Title**: 100% Decision Explanation Trace Completeness
* **Source FR**: `FR-XAI-001`, `FR-XAI-002`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: XAI Quality
* **Requirement**: $100.0\%$ of evaluated payment intents shall generate a complete `decision_trace` object containing top-3 feature attributions and a natural language text summary.
* **Rationale**: High-stakes FinTech security forbids opaque rejections; every decision must be auditable and explainable.
* **Metric & Target**: $100.0\%$ Explanation Completeness ($0$ decisions rendered without XAI trace).
* **Measurement Method**: Automated schema validation over all audit log decision entries.
* **Acceptance Criteria**: 10,000 processed intents yield 10,000 valid XAI traces.
* **Dependencies**: `FR-XAI-001`, `FR-XAI-002`.

---

### NFR-XAI-002: XAI Text Synthesis Latency SLA
* **NFR ID**: `NFR-XAI-002`
* **Title**: XAI Natural Language Text Synthesis Latency SLA
* **Source FR**: `FR-XAI-002`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: XAI Performance
* **Requirement**: Feature attribution ranking and natural text explanation synthesis shall complete in $\le 10\text{ ms}$ ($p_{99}$).
* **Rationale**: Pre-computed template text injection avoids expensive LLM calls during inference path.
* **Metric & Target**: $p_{99}$ Latency $\le 10\text{ ms}$.
* **Measurement Method**: Server-side execution timer around XAI synthesis function.
* **Acceptance Criteria**: 99% of explanation synthesis calls complete in $\le 10\text{ ms}$.
* **Dependencies**: `FR-XAI-002`.
