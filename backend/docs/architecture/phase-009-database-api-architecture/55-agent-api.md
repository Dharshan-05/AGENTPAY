# AGENTPAY — 55: Autonomous Agent Management REST Endpoints Specification

## 1. Agent API Endpoints

* `POST /api/v1/agents`: Enroll new agent principal.
* `GET /api/v1/agents`: List tenant agents with pagination.
* `GET /api/v1/agents/{agent_id}`: Retrieve agent profile & autonomy level.
* `POST /api/v1/agents/{agent_id}/suspend`: Emergency suspend agent execution.
* `POST /api/v1/agents/{agent_id}/resume`: Resume suspended agent.
* `POST /api/v1/agents/{agent_id}/capabilities`: Assign capability scopes.
