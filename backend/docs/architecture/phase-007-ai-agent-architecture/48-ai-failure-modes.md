# AGENTPAY — 48: Fail-Closed AI Service Failure Playbooks

## 1. Fail-Closed Fallback Rules

If any AI / ML microservice fails, times out, or returns corrupt outputs:

1. **LLM Service Outage**: System attempts single retry; if unavailable, task halts with `ERR_LLM_UNAVAILABLE`. No payment execution occurs.
2. **FRAUDGUARD Risk Service Outage**: AGENTGUARD switches to deterministic static policy rules and assigns minimum `MEDIUM_RISK` score, holding intents for human `REVIEW`. System NEVER defaults to `ALLOW`.
3. **AGENTGUARD Control Plane Outage**: API Gateway fail-closed circuit breaker rejects all agent payment proposals (`HTTP 503 Service Unavailable`).
