# AGENTPAY — 02: 30 Non-Negotiable Payment Design Principles

## 1. Design Principles Overview

```
+-----------------------------------------------------------------------+
|                 30 NON-NEGOTIABLE PAYMENT DESIGN PRINCIPLES           |
+-----------------------------------------------------------------------+
|  1. Absolute Financial Correctness (Zero Over-Refund / Zero Over-Spend)|
|  2. Multi-Tier Idempotency Locking (24h Redis Lock on idempotency_key)|
|  3. Explicit Payment Authorization (Short-Lived Authorization Token)  |
|  4. Strong Consistency for Financial State Machine Transitions        |
|  5. Eventual Consistency for Telemetry & Analytics Dashboard Streams  |
|  6. Strict State-Machine Controlled Transaction Processing             |
|  7. Fail-Closed Security Default (Outages Default to BLOCK/REVIEW)    |
|  8. Append-Only Immutable Block Hash Audit Logging Chain              |
|  9. Abstract Payment Provider Interface (IPaymentProvider Adapter)   |
| 10. Zero-Trust Security Boundaries Across Gateway & Internal Services|
| 11. Scoped Capability Least Privilege (spend:intent_create)           |
| 12. Defense in Depth Across Gateway, AGENTGUARD & Provider Rails      |
| 13. Dual Real-Time & Scheduled Nightly Webhook Reconciliation Jobs   |
| 14. OpenTelemetry W3C Distributed Payment Tracing                     |
| 15. Server-Side Payment Emergency Kill Switch Execution               |
| 16. Structural Decoupling of Order Creation vs Payment Settlement    |
| 17. Multi-Attempt Payment Tracking & Retry Backoff Controls           |
| 18. Hard 5,000ms Gateway Provider Timeout SLA                         |
| 19. Authoritative PAYMENT_STATUS_UNKNOWN State Resolution Protocol    |
| 20. Mandatory Webhook HMAC-SHA256 Signature Verification              |
| 21. Single-Use Webhook Event Deduplication & Replay Protection        |
| 22. Double-Entry Accounting Ledger Engine (Sum Debit = Sum Credit)    |
| 23. Cumulative Partial Refund Amount Guard Rails                      |
| 24. Separation of Risk Scoring, Policy Rules & Execution Authority    |
| 25. Normalized 13-Category Internal Payment Error Model               |
| 26. Transactional Event Outbox Pattern for Atomic Message Publishing  |
| 27. PostgreSQL Row-Level Security (RLS) Multi-Tenant Data Isolation   |
| 28. Integer Minor Unit Financial Precision (Zero Floating Point)      |
| 29. Authoritative Payment Status Notification Generation              |
| 30. Zero Payment Secret Exposure to Frontend / AI LLM Contexts        |
+-----------------------------------------------------------------------+
```
