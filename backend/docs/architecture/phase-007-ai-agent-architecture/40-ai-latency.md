# AGENTPAY — 40: Latency Budgets & Parallel Feature Extraction SLA

## 1. Subsystem Latency Budget Allocations

$$\text{Total Internal Latency } p_{99} \le 100\text{ ms}$$

* **API Gateway Route & Verification**: $\le 15\text{ ms}$.
* **AGENTGUARD Deterministic Policy Check**: $\le 15\text{ ms}$.
* **FRAUDGUARD 12-D Feature Extraction**: $\le 20\text{ ms}$ (Parallel Redis/DB queries).
* **XGBoost Anomaly Model Scoring**: $\le 30\text{ ms}$.
* **SHAP & Natural Text Explanation Synthesis**: $\le 10\text{ ms}$.
