# AGENTPAY — 01: Core AI System Objectives & Non-Negotiable Boundaries

## 1. System Objectives

The primary objective of the AGENTPAY + AGENTGUARD AI Architecture is to enable autonomous AI agents to plan, discover, compare, and assemble commerce transactions while maintaining absolute financial safety, explainability, and policy compliance.

---

## 2. Non-Negotiable AI Rules

1. **LLM Is Not a Security Authority**: Large Language Models (LLMs) are probabilistic reasoning components, NOT security or authorization decision makers.
2. **LLM Is Not a Payment Authority**: An LLM cannot execute payments directly. It generates structured proposal payloads (`PAYMENT INTENT`).
3. **Mandatory AGENTGUARD Interception**: Every payment intent proposal must pass through AGENTGUARD policy checks, FRAUDGUARD risk scoring, and Payment Orchestration before reaching payment rails.
4. **Authoritative Status Verification**: Payment success/failure status is strictly determined by Razorpay API webhooks and relational database records, NEVER by LLM text output.
5. **Zero Raw Credentials in Context**: Raw credit card numbers, UPI PINs, or banking passwords are NEVER injected into LLM prompt contexts.
