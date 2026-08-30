# AGENTPAY — 49: 20 Non-Negotiable REST API Design Principles

## 1. Architectural Principles Overview

```
+-----------------------------------------------------------------------+
|                 20 NON-NEGOTIABLE REST API DESIGN PRINCIPLES          |
+-----------------------------------------------------------------------+
|  1. Resource-Oriented REST Naming & Standard HTTP Verbs (GET, POST)   |
|  2. Explicit URI Path Versioning (/api/v1/...)                        |
|  3. Zero Trust Multi-Actor Authentication (JWT, mTLS, HMAC Key Pairs) |
|  4. Fine-Grained Authorization (RBAC + ABAC + Agent Capability Scopes)|
|  5. Trusted Server-Side Tenant Context Extraction (Zero Client Trust) |
|  6. Mandatory Request Header Idempotency on State-Mutating Endpoints   |
|  7. Strict Ingress Request Schema Validation (Zod / OpenAPI 3.0)       |
|  8. Standardized Internal Error Model JSON Response Structure        |
|  9. Explicit Command Endpoints for Financial Actions (/authorize)     |
| 10. Opaque Cursor-Based Pagination on High-Volume List Endpoints      |
| 11. Multi-Tier Sliding Window Rate Limiting (Tenant + Actor Scoped)   |
| 12. Complete Request Tracing Context Injection (trace_id, request_id)|
| 13. Synchronous < 5ms Webhook Signature Verification Endpoint        |
| 14. Server-Authoritative Field Enforcement (Status, Risk Score)       |
| 15. Mass-Assignment Request Payload Parameter Sanitization           |
| 16. OpenTelemetry Distributed Tracing Instrumentation Across Spans    |
| 17. Security Audit Logging on 100% of Financial Mutation Endpoints    |
| 18. OpenAPI 3.0 Contract Governance & Automated Schema Testing       |
| 19. Backward-Compatible Contract Evolution & Deprecation Headers     |
| 20. Fail-Closed Security Response Defaults on Inter-Service Outages   |
+-----------------------------------------------------------------------+
```
