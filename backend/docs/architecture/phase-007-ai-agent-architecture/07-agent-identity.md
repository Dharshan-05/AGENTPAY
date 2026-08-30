# AGENTPAY — 07: Agent Principal Identity & LLM Model Abstraction

## 1. Identity vs Model Decoupling

$$\text{LLM Model} \neq \text{Agent Identity}$$

In AGENTPAY, an AI AGENT is an independently verifiable security principal (`agent_id`, `tenant_id`, `owner_id`) backed by assigned cryptographic HMAC secrets and capability scopes. The underlying LLM model (e.g. GPT-4o, Claude 3.5 Sonnet, Llama 3) is merely an interchangeable reasoning engine that can be routed dynamically without altering the agent's identity, permissions, or historical audit trail.

---

## 2. Identity Schema

```typescript
export interface IAgentPrincipal {
  agent_id: string;          // agt_8f9b2c3a-4e1d-4a5b
  tenant_id: string;         // tenant_7f8a9b0c
  owner_id: string;          // usr_91a0b2c3
  agent_type: string;        // COMMERCE_AGENT
  status: AgentStatus;       // ACTIVE | SUSPENDED | REVOKED
  capabilities: string[];    // ["product:search", "spend:intent_create"]
  policy_id: string;         // pol_123456
  trust_score: number;       // 85 (0-100)
}
```
