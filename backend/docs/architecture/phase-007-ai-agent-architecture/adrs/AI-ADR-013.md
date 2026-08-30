# AI-ADR-013: SHAP Feature Attribution & Natural Text Explanation Synthesis

## Context & Problem Statement
Black-box AI fraud decisions frustrate users and obscure policy enforcement rationale.

## Decision
Utilize SHAP to calculate feature attribution weights for every FRAUDGUARD risk score, converting top contributing features into natural language user explanations.

## Consequences & Trade-Offs
* **Benefits**: 100% decision transparency and auditability.
* **Trade-Offs**: Adds ~10ms for SHAP tree explainer calculation.
