# AGENTPAY — 04: Specialist Agent Taxonomy

## 1. Specialist Agent Classifications

AGENTPAY utilizes a specialized multi-agent taxonomy under a central Orchestrator Supervisor:

1. **Commerce Agent (`COMMERCE_AGENT`)**: Parses user commerce tasks, searches merchant catalogs, compares items, constructs shopping cart payloads, and formats payment intent proposals.
2. **Payment Agent (`PAYMENT_AGENT`)**: Formats payment payloads, verifies payment authorization contexts, interacts with Payment Orchestrator adapters, and tracks transaction state machine transitions.
3. **Security Agent (`SECURITY_AGENT`)**: Monitors agent action velocity, detects prompt injection anomalies, triggers compromised agent containment playbooks, and manages Emergency Stop states.
4. **Risk Agent (`RISK_AGENT`)**: Computes 12-D feature vectors, invokes the FRAUDGUARD XGBoost risk model, calculates SHAP feature attributions, and generates natural text decision summaries.
5. **Support Agent (`SUPPORT_AGENT`)**: Handles user queries regarding policy limits, transaction histories, refund statuses, and XAI decision explanations.
