# AGENTPAY — 01: Core Payment System Objectives & Boundary Rules

## 1. Core Objectives

The primary objective of the AGENTPAY Payment Architecture is to establish a production-grade, highly reliable, fail-closed payment orchestration platform for autonomous AI agents and human users.

---

## 2. Non-Negotiable Payment Boundary Rules

1. **LLM Never Executes Payments**: LLM reasoning models are strictly prohibited from calling payment APIs directly or accessing payment credentials.
2. **AI Agent Never Calls Razorpay Directly**: AI agents generate structured proposals (`PaymentIntent`). Only the Payment Orchestrator interacts with Razorpay.
3. **Mandatory AGENTGUARD Interception**: Every payment intent must pass through AGENTGUARD policy rules, FRAUDGUARD risk scoring, and Payment Authorization before settlement dispatch.
4. **Mandatory Idempotency**: All payment-creating and refund-executing requests must enforce Redis 24-hour distributed idempotency locking.
5. **No Floating-Point Money**: Money is represented strictly as integer minor units (e.g. ₹100.00 = `10000`) or PostgreSQL `NUMERIC(18,4)`.
6. **Immutable Financial History**: Historical payment records, ledger entries, and audit logs are append-only and immutable.
