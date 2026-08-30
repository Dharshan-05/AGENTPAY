# AGENTPAY — 06: Payment Orchestrator Component Specifications

## 1. Component Boundaries

The **Payment Orchestrator** is the exclusive internal service boundary authorized to interact with payment gateway adapters.

```
+-----------------------------------------------------------------------+
|                         PAYMENT ORCHESTRATOR                          |
+-----------------------------------------------------------------------+
|  1. Ingress Authorization Token Verification                          |
|  2. Multi-Tier Idempotency Lock Acquisition (24h Redis SETNX)         |
|  3. Server-Side Amount, Currency & Merchant Validation                |
|  4. 18-State Payment Transaction Machine Execution                    |
|  5. Razorpay Adapter Payload Dispatch & Timeout Management             |
|  6. Event Outbox Persistence & Asynchronous Worker Notification        |
+-----------------------------------------------------------------------+
```

AI agents, web frontends, and external microservices possess zero authorization to bypass the Payment Orchestrator or call Razorpay directly.
