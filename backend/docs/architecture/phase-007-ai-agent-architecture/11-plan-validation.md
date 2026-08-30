# AGENTPAY — 11: Deterministic Plan Schema & Capability Pre-Execution Validation

## 1. Plan Validation Engine

LLM-generated plans are NEVER executed blindly. Every proposed plan passes through a 5-step deterministic validator before any step execution:

$$\text{LLM Plan} \rightarrow \text{Schema Verification} \rightarrow \text{Unknown Tool Rejection} \rightarrow \text{Scope Check} \rightarrow \text{Amount Cap Check} \rightarrow \text{Execution}$$

---

## 2. Rejection Rules

Plans are rejected instantly if they exhibit:
1. Unknown tool names or unregistered functions.
2. Missing mandatory parameters (`amount`, `currency`, `idempotency_key`).
3. Intent amounts exceeding assigned single limit policy caps.
4. Requested capabilities not held by the calling `agent_id`.
