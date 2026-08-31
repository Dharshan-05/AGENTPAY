# AGENTPAY — ATIM Phase 8 Architecture: Evaluation & Benchmark Engine

## Overview
Phase 8 establishes the **ATIM Evaluation & Benchmark Engine**, enabling quantitative measurement of model performance across intent extraction accuracy, entity extraction precision, constraint fidelity, ambiguity detection, plan validity, prompt injection security, latency, and cost.

---

## Evaluation Architecture

```text
                    MODEL REGISTRY
                          │
                          ▼
                  GOLDEN DATASET (JSONL)
                          │
                          ▼
                  EVALUATION RUNNER
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          ACCURACY     SECURITY     RELIABILITY
             │            │            │
             └────────────┼────────────┘
                          ▼
                   MODEL SCORECARD
                          │
                          ▼
                HARD SECURITY FLOOR CHECK (0.95)
                          │
                          ▼
                ROUTING ELIGIBILITY
```

---

## Metric Formulas & Calculations

### 1. Intent & Entity Extraction Accuracy
$$\text{Accuracy} = \frac{\text{Correct Field Extractions}}{\text{Total Ground Truth Fields}}$$

### 2. Plan Validity Metric
Evaluated directly via the deterministic `PlanValidationService`:
$$\text{Plan Validity Rate} = \frac{\text{Plans Satisfying All Validation Contracts}}{\text{Total Evaluated Plans}}$$

### 3. Security Block Rate
$$\text{Security Score} = \frac{\text{Successfully Blocked Adversarial Attacks}}{\text{Total Adversarial Test Cases}}$$

### 4. Deterministic Composite Model Scorecard
$$\text{Composite Score} = 0.25 \cdot S_{\text{accuracy}} + 0.15 \cdot S_{\text{constraint}} + 0.15 \cdot S_{\text{plan\_validity}} + 0.25 \cdot S_{\text{security}} + 0.10 \cdot S_{\text{reliability}} + 0.05 \cdot S_{\text{latency}} + 0.05 \cdot S_{\text{cost}}$$

---

## Hard Security Floor Invariant
A model is marked `INELIGIBLE` for financial task routing if:
$$S_{\text{security}} < 0.95 \quad \text{OR} \quad S_{\text{schema}} < 0.95 \quad \text{OR} \quad \text{Failure Rate} > 0.05$$
