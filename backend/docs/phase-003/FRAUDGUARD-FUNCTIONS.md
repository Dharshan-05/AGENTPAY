# AGENTPAY — FRAUDGUARD Risk Engine Functional Specifications

## 1. Overview

**FRAUDGUARD** is the explainable AI fraud detection and transaction risk engine of AGENTPAY. It extracts 12 real-time risk feature dimensions and executes statistical anomaly scoring to derive normalized `RISK SCORE` (0 - 100) values.

---

## 2. Specifications

### FR-FRD-001: 12-Dimensional Risk Feature Vector Extraction
* **FR ID**: `FR-FRD-001`
* **Title**: 12-Dimensional Risk Feature Extraction Pipeline
* **Source**: `REQ-FRAUD-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: FRAUDGUARD Engine (`FRAUDGUARD`)
* **Goal**: Compute 12 standardized risk features for an incoming payment intent.
* **Preconditions**: Intent passed preliminary AGENTGUARD checks (`ALLOW` or `REVIEW`).
* **Trigger**: Ingestion into FRAUDGUARD pipeline phase.
* **Inputs**: `intent` object, `agent_history` DB records, `redis_velocity_counters`.
* **Main Flow**:
  1. Engine fetches Redis velocity counters (`velocity_60s`, `velocity_15m`).
  2. Engine queries merchant trust registry for `merchant_trust_score`.
  3. Engine fetches MCC risk weight (`category_risk_weight`).
  4. Engine computes $Z$-score of `intent.amount` against historical agent 30-day mean:
     $$Z = \frac{\text{amount} - \mu_{30\text{d}}}{\sigma_{30\text{d}}}$$
  5. Engine computes ratio of intent amount to user historical average purchase size (`user_baseline_ratio`).
  6. Engine evaluates off-hours flag, geo-mismatch flag, and historical agent failure rate.
  7. Engine aggregates features into normalized 12-dimensional vector $\mathbf{x} \in \mathbb{R}^{12}$.
* **Performance SLA**: Feature vector calculation completes in $\le 20\text{ ms}$ ($p_{99}$).
* **Outputs**: 12-Dimensional Feature Vector $\mathbf{x}$.
* **Audit Events**: `EVENT_FEATURES_EXTRACTED`.
* **Acceptance Criteria**: `AC-FRAUD-001`.
* **Dependencies**: `FR-AGD-001`.

---

### FR-FRD-002: Statistical Anomaly & Risk Score Calculation
* **FR ID**: `FR-FRD-002`
* **Title**: Statistical Anomaly Scoring & Normalized Risk Score Calculation
* **Source**: `REQ-FRAUD-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: FRAUDGUARD Engine (`FRAUDGUARD`)
* **Goal**: Map feature vector $\mathbf{x}$ to normalized `RISK SCORE` (0-100) and `FRAUD PROBABILITY` ($0.00 - 1.00$).
* **Preconditions**: Feature vector extracted via `FR-FRD-001`.
* **Trigger**: Feature extraction pipeline completion.
* **Inputs**: Feature Vector $\mathbf{x}$.
* **Main Flow**:
  1. Engine evaluates statistical anomaly classifier over feature vector $\mathbf{x}$.
  2. Engine outputs raw raw probability score $P_{\text{fraud}} \in [0.00, 1.00]$.
  3. Engine scales probability to normalized integer `risk_score`:
     $$\text{risk\_score} = \text{round}(P_{\text{fraud}} \times 100)$$
  4. Engine assigns risk level according to threshold matrix:
     * `00 - 35`: `LOW_RISK`
     * `36 - 69`: `MEDIUM_RISK`
     * `70 - 89`: `HIGH_RISK`
     * `90 - 100`: `CRITICAL_RISK`
* **Performance SLA**: Scoring completes in $\le 30\text{ ms}$ ($p_{99}$).
* **Outputs**: Risk Scoring Output object (`risk_score`, `fraud_probability`, `risk_level`).
* **Audit Events**: `EVENT_RISK_SCORED`.
* **Acceptance Criteria**: `AC-FRAUD-001`.
* **Dependencies**: `FR-FRD-001`.
