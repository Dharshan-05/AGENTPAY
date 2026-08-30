# AGENTPAY — 90: Target Sub-100ms API Latency & Query Budget SLA

## 1. Internal Subsystem SLA Allocations

$$\text{Internal System API Latency } p_{99} \le 100\text{ ms}$$

* **API Gateway & JWT Auth Check**: $\le 15\text{ ms}$.
* **AGENTGUARD Policy Evaluation**: $\le 15\text{ ms}$.
* **FRAUDGUARD XGBoost Risk Scoring**: $\le 30\text{ ms}$.
* **PostgreSQL Database Transaction**: $\le 20\text{ ms}$.
* **Response Serialization**: $\le 10\text{ ms}$.
