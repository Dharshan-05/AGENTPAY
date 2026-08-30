# AGENTPAY — Payment Requirements

## 1. Overview

Payment requirements establish functional, structural, and safety specifications for handling financial transactions within AGENTPAY. These rules guarantee that no payment can be executed without passing through the complete AGENTGUARD and FRAUDGUARD trust pipeline.

---

## 2. Requirement Baseline

### 2.1 Pre-Execution Pipeline Enforcement
* **REQ-PAY-001**: Direct communication between an AI AGENT and payment gateways is strictly forbidden. All payment requests must flow through the canonical 15-step Payment Trust Pipeline:
  $$\text{Agent Intent} \longrightarrow \text{AGENTGUARD} \longrightarrow \text{FRAUDGUARD} \longrightarrow \text{Authorization} \longrightarrow \text{Payment Execution}$$
* **REQ-PAY-002**: The payment execution service shall verify that a `PAYMENT INTENT` possesses a valid `AUTHORIZED` state token containing digital cryptographic signatures from AGENTGUARD and FRAUDGUARD before dispatching settlement payloads to payment rails.

### 2.2 Payment Gateway Abstraction & Adapters
* **REQ-PAY-003**: The system shall implement a Payment Adapter Interface decoupling internal intent logic from specific payment providers.
* **REQ-PAY-004**: For the hackathon MVP, the payment layer shall support two distinct execution adapters:
  1. **Simulator Adapter**: Instant mock settlement with configurable success/failure rates for live testing.
  2. **Razorpay Test Mode Adapter**: Real-world integration with Razorpay API sandbox for INR test payments.
* **REQ-PAY-005**: The payment adapter architecture shall support seamless extension to direct UPI settlement, credit card networks, and net banking APIs in future phases.

### 2.3 Payment Intent Lifecycle & State Machine
* **REQ-PAY-006**: The system shall track and enforce valid state transitions for every `PAYMENT INTENT`:
  $$\text{CREATED} \rightarrow \text{POLICIED} \rightarrow \text{SCORED} \rightarrow \begin{cases} \text{AUTHORIZED} \\ \text{PENDING\_APPROVAL} \\ \text{REJECTED} \end{cases} \rightarrow \text{PROCESSING} \rightarrow \begin{cases} \text{EXECUTED} \\ \text{FAILED} \end{cases}$$
* **REQ-PAY-007**: State transitions shall be atomic and recorded in append-only database transaction tables.

### 2.4 Idempotency & Double-Spend Safeguards
* **REQ-PAY-008**: The payment processing service shall enforce strict idempotency on `idempotency_key` headers.
* **REQ-PAY-009**: The system shall acquire a distributed lock (via Redis) on `idempotency_key` during intent processing to prevent race conditions or concurrent double-spending attempts.

### 2.5 Error Handling, Timeouts & Failure Recovery
* **REQ-PAY-010**: If a payment processor fails to respond within 5,000 ms, the system shall mark the payment intent as `FAILED (ERR_GATEWAY_TIMEOUT)` and release reserved balance locks.
* **REQ-PAY-011**: Automatic retries against payment processors shall be strictly limited to a maximum of 2 attempts using exponential backoff with jitter.
* **REQ-PAY-012**: If a payment execution fails mid-flight, the system shall log a reconciliation event and notify the user dashboard immediately.

### 2.6 Refund & Cancellation Abstraction
* **REQ-PAY-013**: The payment layer shall support an intent cancellation endpoint (`POST /api/v1/payment-intents/{id}/cancel`) for intents in `PENDING_APPROVAL` status.
* **REQ-PAY-014**: The system shall log refund requests initiated by merchants or users and reconcile refund transaction status back to the original intent audit record.
