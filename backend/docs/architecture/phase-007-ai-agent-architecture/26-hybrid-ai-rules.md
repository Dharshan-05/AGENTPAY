# AGENTPAY — 26: Hybrid AI Planning + Deterministic Rules + ML Scoring Engine

## 1. Hybrid Decision Pipeline

```
[ LLM Agent Proposal ] ──> [ Deterministic Rules (Single Limit / Category) ] ──> [ XGBoost Risk Model ] ──> [ AGENTGUARD Aggregator ] ──> ALLOW/REVIEW/BLOCK
```

The system combines probabilistic LLM reasoning with deterministic hard business rules and ML anomaly scoring. Deterministic hard rules override both LLM outputs and ML predictions.
