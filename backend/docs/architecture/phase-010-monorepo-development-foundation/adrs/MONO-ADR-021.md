# MONO-ADR-021: Razorpay Sandbox Adapter & Mock Integration Strategy

## 1. Context & Problem Statement
Testing payment flows without using real funds or production payment gateway endpoints.

## 2. Decision
Integrate Razorpay Test Mode keys (`rzp_test_*`) for sandbox testing and provide an offline `MockPaymentAdapter` for unit/integration test suites.

## 3. Consequences & Trade-Offs
* **Benefits**: Enables deterministic offline testing with zero live financial impact.
* **Trade-Offs**: Requires keeping mock adapters synchronized with real gateway API payloads.
