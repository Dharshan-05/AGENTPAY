# PAY-ADR-002: Abstract `IPaymentProvider` Adapter Pattern Interface

## Context & Problem Statement
Coupling core payment logic directly to Razorpay API specifics makes supporting alternative gateways difficult.

## Decision
Define an abstract `IPaymentProvider` interface that exposes generic payment functions (`createOrder`, `executePayment`, `refundPayment`, `verifyWebhookSignature`).

## Consequences & Trade-Offs
* **Benefits**: Decouples business logic from gateway specifics; enables seamless provider swapping.
* **Trade-Offs**: Requires mapping provider-specific responses to normalized domain models.
