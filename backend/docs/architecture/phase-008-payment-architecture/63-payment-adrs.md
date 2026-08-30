# AGENTPAY — 63: Index of 20 Payment Architecture Decision Records (`adrs/`)

## 1. ADR Summary Index

| ADR ID | Title | Core Decision Summary |
| :--- | :--- | :--- |
| **PAY-ADR-001**| Payment Orchestrator | Exclusive internal boundary for payment provider settlement calls |
| **PAY-ADR-002**| Provider Abstraction | Abstract `IPaymentProvider` interface for multi-gateway support |
| **PAY-ADR-003**| Razorpay Adapter | Encapsulates Razorpay API endpoints & signature verification |
| **PAY-ADR-004**| Payment Intent | Decoupled `PaymentIntent` entity for intent proposal handling |
| **PAY-ADR-005**| Payment Authorization | Cryptographic short-lived (15m) authorization context token |
| **PAY-ADR-006**| Payment State Machine | 18-state deterministic transaction machine with strict rules |
| **PAY-ADR-007**| Idempotency | Redis 24-hour distributed lock on `idempotency_key` |
| **PAY-ADR-008**| Duplicate Prevention | 4-layer defense-in-depth double-spend prevention |
| **PAY-ADR-009**| Concurrency Control | PostgreSQL pessimistic row locking (`FOR UPDATE`) |
| **PAY-ADR-010**| Money Precision | Minor unit 64-bit integer math & PostgreSQL `NUMERIC` |
| **PAY-ADR-011**| Currency Handling | ISO 4217 currency validation; implicit conversion banned |
| **PAY-ADR-012**| Webhook Security | HMAC-SHA256 signature check & 7-day event deduplication |
| **PAY-ADR-013**| Refund Architecture | Cumulative partial refund amount cap tracking |
| **PAY-ADR-014**| Financial Ledger | Append-only, immutable accounting log for financial entries |
| **PAY-ADR-015**| Reconciliation | Real-time webhook + nightly batch settlement reconciliation |
| **PAY-ADR-016**| Event Outbox | Transactional outbox pattern for atomic event publishing |
| **PAY-ADR-017**| Payment Risk | FRAUDGUARD 12-D ML risk score integration |
| **PAY-ADR-018**| Human Approval | Interactive escalation cards in Approval Center UI |
| **PAY-ADR-019**| Payment Kill Switch | Multi-tier emergency payment freeze propagation |
| **PAY-ADR-020**| Provider Failure Recovery| Fail-closed circuit breaker & `PAYMENT_STATUS_UNKNOWN` state |
