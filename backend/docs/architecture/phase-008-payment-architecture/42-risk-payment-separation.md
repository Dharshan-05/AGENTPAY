# AGENTPAY — 42: Structural Decoupling of Risk, Policy & Authorization

## 1. Decoupled Pipeline

$$\text{FRAUDGUARD (Risk Score)} \rightarrow \text{Policy Engine (Business Rules)} \rightarrow \text{Payment Authorization (Token)} \rightarrow \text{Payment Orchestrator (Settlement)}$$

Decoupling ensures that risk scores inform policy decisions, but risk scores do not execute payments directly.
