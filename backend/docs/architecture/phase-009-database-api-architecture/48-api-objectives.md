# AGENTPAY — 48: API Core Architectural Objectives & Safety Rules

## 1. Core API Objectives

The primary objective of the AGENTPAY REST API Architecture is to expose secure, typed, versioned, idempotent HTTP endpoint contracts for AI agents, merchants, users, and administrators.

---

## 2. Non-Negotiable API Safety Rules

1. **LLM Output Untrusted**: API controllers treat all AI agent payloads as untrusted user input, enforcing Zod schema validation before domain processing.
2. **Server-Authoritative Status**: Clients and agents are strictly prohibited from mutating payment status, risk scores, or ledger balances directly.
3. **Mandatory Ingress Authentication**: 100% of non-public endpoints enforce OAuth2 / JWT or HMAC request signature verification.
4. **Mandatory Idempotency**: All payment creation, execution, and refund endpoints require valid `Idempotency-Key` headers.
5. **No Arbitrary Financial PATCH Operations**: Generic `PATCH /payments/{id}` endpoints are forbidden. Mutations occur strictly through explicit command endpoints (`/authorize`, `/execute`, `/refund`).
