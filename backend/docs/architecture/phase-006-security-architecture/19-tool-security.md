# AGENTPAY — 19: Agent Tool Schema Validation & Capability Scopes

## 1. Tool Security Controls

Every tool exposed to an AI agent (e.g. `create_payment_intent`, `query_transaction_status`) must be explicitly registered and schema-validated.

```json
{
  "tool_id": "tool_create_payment_intent",
  "name": "create_payment_intent",
  "required_scope": "spend:intent_create",
  "input_schema": {
    "type": "object",
    "required": ["amount", "currency", "merchant_name", "merchant_domain", "category", "idempotency_key"],
    "properties": {
      "amount": { "type": "integer", "minimum": 1 },
      "currency": { "type": "string", "enum": ["INR"] }
    }
  },
  "risk_level": "HIGH",
  "audit_enabled": true
}
```

---

## 2. Tool Output Sanitization

Tool outputs returned from external APIs are sanitized before being fed back into agent memory to prevent secondary prompt injection attacks.
