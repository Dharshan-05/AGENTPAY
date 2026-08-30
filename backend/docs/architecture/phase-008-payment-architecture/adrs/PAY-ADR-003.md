# PAY-ADR-003: Razorpay Adapter Gateway Integration

## Context & Problem Statement
Integrating Razorpay requires handling custom API payloads, HMAC signatures, and error codes.

## Decision
Implement a dedicated `RazorpayAdapter` class implementing `IPaymentProvider` that encapsulates all Razorpay API client interactions.

## Consequences & Trade-Offs
* **Benefits**: Keeps Razorpay SDK dependencies isolated within a single adapter module.
* **Trade-Offs**: Requires updating adapter code when Razorpay updates API versions.
