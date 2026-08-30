# AGENTPAY — 12: Dynamic Task-Based Model Router

## 1. Model Routing Architecture

The Model Router dynamically assigns tasks to optimal LLM / ML models based on complexity, latency SLAs, cost budgets, and risk thresholds.

```mermaid
graph TD
    TASK[Task Request] --> ROUTE{Evaluate Task Type & Risk}
    ROUTE -- Intent Classification --> M1[Fast Lightweight Model: gpt-4o-mini / Llama-3-8B]
    ROUTE -- Complex Decomposition --> M2[Reasoning Engine: gpt-4o / Claude 3.5 Sonnet]
    ROUTE -- Risk Scoring --> M3[Deterministic ML Service: XGBoost Classifier]
    ROUTE -- Policy Enforcement --> M4[Deterministic Policy Engine: TypeScript Rules]
```

---

## 2. Security Mandate

Deterministic policy enforcement and fraud scoring NEVER route to generative LLM models. Policy rules execute via TypeScript code; fraud scoring executes via XGBoost.
