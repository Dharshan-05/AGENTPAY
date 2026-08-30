# AGENTPAY — 25: Typed HTTP API Client Library Architecture

## 1. API Client Specification

Frontend consumes a typed API client wrapping `fetch` / `axios`:

```typescript
export class AgentPayClient {
  constructor(private baseUrl: string, private getToken: () => string) {}

  async createPaymentIntent(payload: CreatePaymentIntentRequest): Promise<PaymentIntentResponse> {
    // Inject Authorization & Idempotency-Key headers
  }
}
```
