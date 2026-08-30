# AGENTPAY — 21: 4-Tier Tool Risk Classification (LOW to CRITICAL)

## 1. Tool Risk Matrix

| Risk Level | Target Tool Examples | Required Controls |
| :--- | :--- | :--- |
| **`LOW`** | `product_search`, `merchant_lookup` | Input schema validation |
| **`MEDIUM`** | `cart_create`, `user_notify` | Input schema validation + Rate limiting |
| **`HIGH`** | `create_payment_intent`, `refund_request` | AGENTGUARD policy check + FRAUDGUARD risk score |
| **`CRITICAL`**| `execute_payment_adapter` | Direct LLM Access Denied; Reserved strictly for Payment Orchestrator |
