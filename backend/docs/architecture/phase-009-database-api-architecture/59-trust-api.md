# AGENTPAY — 59: Agent Trust Score Evaluation REST API Endpoints

## 1. Trust API Endpoints

* `GET /api/v1/trust/agents/{agent_id}`: Fetch real-time trust score (0-100) and historical trust trajectory for target agent principal.
* `POST /api/v1/trust/evaluations`: Trigger manual trust score re-calculation.
