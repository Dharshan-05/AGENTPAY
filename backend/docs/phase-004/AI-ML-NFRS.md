# AGENTPAY — AI/ML Quality Non-Functional Requirements

## 1. Overview

AI/ML Quality requirements define model accuracy targets, false positive/negative risk tradeoffs, model drift monitoring SLAs, and inference latency limits.

---

## 2. Requirement Baseline

### NFR-AML-001: Fraud Model False Positive Rate Target
* **NFR ID**: `NFR-AML-001`
* **Title**: Maximum 2.0% False Positive Rate Target for FRAUDGUARD
* **Source FR**: `FR-FRD-002`
* **Priority**: P1 | **Target Horizon**: PROTOTYPE TARGET
* **Category**: AI/ML Quality
* **Requirement**: The FRAUDGUARD risk scoring classifier shall achieve a false positive rate of $< 2.0\%$ on standard validation benchmark datasets.
* **Rationale**: High false positive rates lead to excessive transaction rejections and user review fatigue.
* **Metric & Targets**:
  * False Positive Rate: $< 2.0\%$
  * ROC-AUC Score Target: $\ge 0.92$
  * Precision Target: $\ge 0.88$ | Recall Target: $\ge 0.90$
* **Measurement Method**: Offline model validation benchmark against synthetic transaction test set.
* **Acceptance Criteria**: Model confusion matrix yields FPR $< 2.0\%$ and ROC-AUC $\ge 0.92$.
* **Dependencies**: `FR-FRD-002`.

---

### NFR-AML-002: Model Fail-Safe Fallback SLA
* **NFR ID**: `NFR-AML-002`
* **Title**: AI Model Inference Timeout & Fail-Safe Fallback Trigger SLA
* **Source FR**: `FR-FRD-002`, `FR-ERR-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: AI/ML Reliability
* **Requirement**: If the ML inference scoring container takes $> 100\text{ ms}$ to respond, the system shall terminate the inference call, execute deterministic rule fallback, and assign minimum `MEDIUM_RISK`.
* **Rationale**: Prevents a hung ML model container from stalling the 100ms payment pipeline SLA.
* **Metric & Target**: Timeout trigger at $100\text{ ms}$; $100\%$ fallback execution.
* **Measurement Method**: Fault injection introducing 500ms artificial delay into ML container.
* **Acceptance Criteria**: Pipeline logs `ERR_AI_MODEL_TIMEOUT`, executes deterministic fallback, and completes in $< 120\text{ ms}$.
* **Dependencies**: `FR-FRD-002`.
