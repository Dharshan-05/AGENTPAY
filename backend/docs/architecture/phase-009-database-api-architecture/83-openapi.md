# AGENTPAY — 83: Complete OpenAPI 3.0 Contract Specification

## 1. OpenAPI 3.0 Header Specification

```yaml
openapi: 3.0.3
info:
  title: AGENTPAY + AGENTGUARD Autonomous Payment API
  version: 1.0.0
  description: Authoritative REST API for zero-trust autonomous agent payments.
servers:
  - url: https://api.agentpay.com/api/v1
    description: Production API Server
paths:
  /payment-intents:
    post:
      summary: Create Payment Intent Proposal
      security:
        - BearerAuth: []
        - AgentHMAC: []
      headers:
        Idempotency-Key:
          schema:
            type: string
            format: uuid
          required: true
```
