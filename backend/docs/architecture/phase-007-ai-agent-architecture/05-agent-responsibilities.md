# AGENTPAY — 05: Agent Responsibility Boundaries & Allowed/Forbidden Matrices

## 1. Agent Responsibility Matrix

| Agent Type | Allowed Actions (CAN) | Forbidden Actions (CANNOT) |
| :--- | :--- | :--- |
| **Commerce Agent** | Search products, compare pricing, assemble cart, propose intent | Modify policies, change budget caps, bypass AGENTGUARD, execute settlement |
| **Payment Agent** | Format payment payload, request payment authorization token | Change payment amount without authorization, bypass risk checks |
| **Security Agent** | Monitor velocity, flag anomalies, trigger kill switches | Modify user balances, execute transactions |
| **Risk Agent** | Extract 12-D features, score fraud probability, generate XAI traces| Directly authorize payments, modify policy rules |
| **Support Agent** | Answer user queries, display XAI traces, explain policies | Execute payments, alter agent credentials |
