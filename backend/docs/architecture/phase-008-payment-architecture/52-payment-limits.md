# AGENTPAY — 52: Multi-Tier Spending Limit Counters in Redis

## 1. Spending Limit Counters

* **Single Transaction Cap**: Verified against `agent_policies` table.
* **Daily Budget Counter**: Redis atomic key `budget:tenant:<tenant_id>:agent:<agent_id>:daily` updated via `INCRBYFLOAT`. Reset automatically at `00:00 UTC`.
