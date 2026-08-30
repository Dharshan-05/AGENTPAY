# AGENTPAY — 34: Per-Action Risk Scoring Engine & Step-Up Requirements

## 1. Action Risk Calculation

Every proposed step in an agent plan receives an `action_risk_score` (0-100) based on target resource sensitivity, financial value, and external side-effects. High-risk actions require Step-Up MFA authentication or human review escalations.
