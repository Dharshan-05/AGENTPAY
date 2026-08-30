# AGENTPAY — 10: Task Decomposition & Structured Action Plan Generation

## 1. Structured Plan Pipeline

When presented with a complex commerce goal (e.g. *"Book flight under ₹15,000"*), the Planner Node decomposes the task into atomic, schema-validated steps.

```json
{
  "plan_id": "plan_9f8a7b6c",
  "agent_id": "agt_8f9b2c3a",
  "goal": "Book flight to Mumbai under ₹15,000",
  "steps": [
    {
      "step_id": 1,
      "action": "search_flights",
      "tool": "tool_search_flights",
      "inputs": { "destination": "BOM", "max_price": 1500000 },
      "risk_level": "LOW",
      "required_scope": "product:search"
    },
    {
      "step_id": 2,
      "action": "select_flight_option",
      "tool": "tool_cart_assemble",
      "inputs": { "flight_id": "FL_6789", "amount": 1250000 },
      "risk_level": "MEDIUM",
      "required_scope": "cart:create"
    },
    {
      "step_id": 3,
      "action": "propose_payment_intent",
      "tool": "tool_create_payment_intent",
      "inputs": { "amount": 1250000, "currency": "INR", "merchant_name": "AirIndia" },
      "risk_level": "HIGH",
      "required_scope": "spend:intent_create"
    }
  ]
}
```
