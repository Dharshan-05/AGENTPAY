# AGENTPAY — 06: Payment Orchestration & Razorpay Gateway Boundary Architecture

## 1. Architectural Boundary & Decoupling

To prevent vendor lock-in and decouple core domain business logic from specific payment providers, AGENTPAY implements a **Payment Orchestrator Boundary**. Core intent processing interacts exclusively with an abstract Payment Adapter Interface.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as AI Agent
    participant GW as API Gateway
    participant Guard as AGENTGUARD Policy Engine
    participant Orch as Payment Orchestrator
    participant Adapter as Razorpay Adapter
    participant Razorpay as Razorpay API
    participant Webhook as Webhook Listener Worker
    participant DB as Relational Database

    Agent->>GW: POST /api/v1/payment-intents (Idempotency-Key: UUID)
    GW->>GW: Verify Redis Idempotency Lock
    GW->>Guard: Evaluate Policy & Risk
    Guard-->>Orch: Decision ALLOW (State: AUTHORIZED)
    Orch->>DB: Atomically update State -> AUTHORIZED
    Orch->>Adapter: Dispatch Authorized Intent Payload
    Adapter->>Razorpay: POST /v1/orders (Create Razorpay Order)
    Razorpay-->>Adapter: Order Created (Order ID: order_123)
    Adapter->>Razorpay: POST /v1/payments/pay (Execute Payment)
    Razorpay-->>Adapter: Payment Authorized (Payment ID: pay_456)
    Adapter-->>Orch: Settlement Result: SUCCESS
    Orch->>DB: Atomically update State -> EXECUTED
    Razorpay--)Webhook: POST /api/v1/webhooks/razorpay (Event: payment.captured)
    Webhook->>Webhook: Verify Razorpay HMAC Webhook Signature
    Webhook->>DB: Reconcile Payment Record State -> RECONCILED
    Webhook->>DB: Append SHA-256 Block Hash Audit Entry
```

---

## 2. Adapter Protocol Interface

The Payment Orchestrator communicates with payment providers via a strict TypeScript interface:

```typescript
export interface IPaymentAdapter {
  createOrder(intent: PaymentIntent): Promise<RazorpayOrderResult>;
  executePayment(orderId: string, payload: SettlementPayload): Promise<SettlementResult>;
  verifyWebhookSignature(payload: string, signature: string, secret: string): boolean;
  cancelIntent(intentId: string): Promise<CancellationResult>;
}
```
