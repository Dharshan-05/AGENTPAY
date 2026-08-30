# AGENTPAY — 20: Centralized Agent Tool Registry & Input/Output Schemas

## 1. Tool Registry Interface

Every tool exposed to AI agents must be registered in the Tool Registry:

```typescript
export interface IAgentTool<TInput, TOutput> {
  tool_id: string;             // tool_create_payment_intent
  name: string;                // create_payment_intent
  version: string;             // v1.2.0
  description: string;         // Generates a payment intent proposal
  risk_level: ToolRiskLevel;   // HIGH
  required_scope: string;      // spend:intent_create
  input_schema: ZodSchema<TInput>;
  output_schema: ZodSchema<TOutput>;
  execute(input: TInput, context: AgentContext): Promise<TOutput>;
}
```
