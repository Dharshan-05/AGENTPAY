# AGENTPAY — 23: AGENTGUARD Integration Interface & Decision Payloads

## 1. Intercept Interface

AGENTGUARD intercepts payment intent proposals emitted by AI agents prior to payment orchestrator execution.

```typescript
export interface IAgentGuardEvaluationRequest {
  intent_id: string;
  agent_id: string;
  tenant_id: string;
  amount: number;
  currency: string;
  merchant_domain: string;
  mcc_category: string;
  prompt_context_hash: string;
}
```

Outputs one of three atomic decisions: `ALLOW`, `REVIEW`, or `BLOCK`.
