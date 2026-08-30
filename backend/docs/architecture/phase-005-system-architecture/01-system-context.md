# AGENTPAY — 01: System Context Architecture Specification

## 1. Executive Overview

This document specifies the **System Context Architecture** for AGENTPAY, AGENTGUARD, and FRAUDGUARD. It defines external system actors, boundary interfaces, input/output data flows, and trust touchpoints.

---

## 2. System Context Diagram

```mermaid
graph TD
    subgraph External Actors
        USER[Human Account Owner]
        AGENT[Autonomous AI Agent]
        MERCHANT[Commercial Payee / Merchant]
        ADMIN[Security & Risk Operator]
    end

    subgraph AGENTPAY Platform Boundary
        GW[API Gateway & Edge Auth]
        ORCH[Agent Orchestrator]
        GUARD[AGENTGUARD Security & Policy Engine]
        FRAUD[FRAUDGUARD Explainable Risk Engine]
        PAY[Payment Orchestrator]
        AUDIT[Immutable Block Hash Audit Store]
        DSH[Web Console & Approval Center]
    end

    subgraph Payment Infrastructure
        RAZORPAY[Razorpay Payment Rails Sandbox / Live]
        BANK[Bank & UPI Networks]
    end

    USER -->|Configures Policies & Responds to Approvals| DSH
    AGENT -->|Submits Signed Payment Intent Payload| GW
    ADMIN -->|Monitors Telemetry & Investigates Alerts| DSH
    GW -->|Authenticates & Rates Limits| ORCH
    ORCH -->|Evaluates Policy Rules| GUARD
    GUARD -->|Extracts Features & Calculates Risk| FRAUD
    FRAUD -->|Returns Decision & XAI Trace| GUARD
    GUARD -->|If ALLOW / User Approved| PAY
    PAY -->|Dispatches Payment Payload| RAZORPAY
    RAZORPAY -->|Settles Funds| BANK
    RAZORPAY -->|Webhook Callback| PAY
    PAY -->|Appends Cryptographic Record| AUDIT
    MERCHANT -->|Receives Settlement & Returns Receipt| PAY
```

---

## 3. Actor & Interface Specifications

### 3.1 Human Account Owner (`USER`)
* **Interface**: HTTPS / Web Dashboard & Mobile Approval App (`Layer 1`).
* **Protocol**: TLS 1.3 / REST API / WebSockets.
* **Capabilities**: Policy configuration, MFA session management, one-click escalation approvals/rejections, Emergency Stop kill switch execution.

### 3.2 Autonomous AI Agent (`AI AGENT`)
* **Interface**: RESTful Agent Gateway API (`POST /api/v1/payment-intents`).
* **Protocol**: TLS 1.3 / HMAC-SHA256 Signed HTTP Headers.
* **Capabilities**: Submitting structured `PAYMENT INTENT` payloads, querying intent statuses, receiving webhook decision callbacks.

### 3.3 Payment Gateway Infrastructure (`RAZORPAY`)
* **Interface**: Razorpay API Sandbox / Live Settlement Gateway.
* **Protocol**: RESTful API / HMAC Webhook Callbacks (`payment.captured`, `payment.failed`).
* **Capabilities**: Processing card/UPI settlements, issuing order tokens, returning transaction fulfillment signals.
