# AGENTPAY — Out of Scope (MVP Deferrals & Future Roadmap)

## 1. Executive Summary

To guarantee delivery of a production-grade, highly reliable, and bulletproof demonstration for the hackathon, **AGENTPAY** explicitly defines items that are out of scope for the Phase 001/MVP execution. 

Attempting to build full banking rails, multi-jurisdictional compliance engines, or speculative cryptocurrency infrastructure during an initial hackathon sprint risks distracting from the core value proposition: **Trusted Autonomous Commerce Policy, Security, Fraud Risk, and XAI Authorization**.

---

## 2. Explicit Out-of-Scope Items for Hackathon MVP

### 2.1 Banking & Financial Infrastructure
* **Full Core Banking License / Account Hosting**: AGENTPAY is an intelligence and policy authorization layer, not a licensed bank or custodian.
* **Direct Real-Money Account Custody**: Storing cash deposits or running direct deposit accounts within AGENTPAY is excluded.
* **Multi-Country Settlement & Forex**: Handling cross-border forex clearing, currency conversion hedges, and international SWIFT routing is excluded for MVP (focus is on domestic INR/Razorpay/UPI abstraction).

### 2.2 Unrestricted / Autonomous Irreversible Actions
* **Unrestricted Autonomous Spending**: Unlimited spending without human ceiling rules or policy boundaries is explicitly forbidden by safety design.
* **Irreversible Immediate Settlement Without Cancellation Hooks**: All payments route through abstracted adapters supporting simulation, cancellation, or hold-until-approval states.

### 2.3 Speculative & Complex Financial Services
* **Cryptocurrency & Web3 Protocols**: Decentralized smart contracts, token swaps, and crypto wallets are excluded to keep focus on mainstream FinTech infrastructure.
* **Credit Lending & Buy-Now-Pay-Later (BNPL) Underwriting**: Issuing credit lines or performing automated underwriting for agent-requested loans is excluded.
* **Insurance Underwriting**: Providing automated risk insurance policies for lost agent funds.

### 2.4 Enterprise & Marketplace Extensions
* **Full ERP / Accounting Software Replacement**: Direct general ledger sync with SAP/Oracle is excluded.
* **Massive Merchant Marketplace Operations**: Hosting an e-commerce platform for merchants; AGENTPAY strictly interfaces with existing payment gateways and merchant endpoints.
* **Autonomous Multi-Agent Swarm Economy**: Inter-agent trading ecosystems where agents hire other agents recursively without human owner oversight.

### 2.5 Regulatory & Certification Claims
* **Formal Production Regulatory Certifications**: Claiming official PCI-DSS Level 1 certification, RBI NBFC licensing, or SOC2 Type II audit compliance. (The platform is *designed with compliance considerations*, not certified).

---

## 3. Future Roadmap Mapping

```
+-----------------------------------------------------------------------+
|  PHASE 001 (NOW)   : Vision, Scope, Architecture & Security Models    |
|  MVP DEMO          : AGENTGUARD, FRAUDGUARD, XAI Engine, Simulator    |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  POST-HACKATHON v1.5: Production Gateway Plugins & SDKs               |
|                      Real-world Merchant API Adapters                 |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  ENTERPRISE v2.0   : Multi-Tenant Enterprise Policy Suites            |
|                      Hardware Enclave Agent Signatures (TEE)          |
|                      Decentralized Identity (DID / VC) for AI Agents  |
+-----------------------------------------------------------------------+
```
