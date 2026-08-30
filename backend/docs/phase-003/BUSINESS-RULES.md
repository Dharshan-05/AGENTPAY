# AGENTPAY — Business Rules Catalog

## 1. Overview

This document formalizes 25 non-negotiable business rules (`BR-001` through `BR-025`) governing system logic, financial safety, authorization boundaries, and architectural execution in AGENTPAY.

---

## 2. Business Rules Catalog

| Rule ID | Rule Name | Description |
| :--- | :--- | :--- |
| **BR-001** | Mandatory Authentication | An unauthenticated AI AGENT request shall be rejected immediately at the API edge before reaching policy or fraud engines. |
| **BR-002** | Auth $\neq$ Authorization | Valid cryptographic signatures prove agent identity ONLY. Signature validity conveys zero implicit financial spending authority. |
| **BR-003** | Preemptive AGENTGUARD Gate | Every payment intent MUST pass AGENTGUARD policy checks prior to invoking payment execution rails. |
| **BR-004** | Risk-Aware Decisioning | High-risk transactions calculated by FRAUDGUARD shall be blocked or escalated regardless of basic policy whitelist passes. |
| **BR-005** | Restrictive Precedence | Restrictive security rules (e.g. Category Blacklist or Limit Breach) ALWAYS override permissive whitelist rules. |
| **BR-006** | Adaptive Step-Up Escalation| Intents exceeding the user's auto-approval ceiling MUST escalate to the Approval Center for human confirmation. |
| **BR-007** | Instant Revocation | Revoking an agent or triggering Emergency Stop MUST purge edge authentication caches in $< 10\text{ ms}$. |
| **BR-008** | Absolute Idempotency | Duplicate intent submissions containing identical `idempotency_key` headers MUST return cached responses without re-executing transactions. |
| **BR-009** | Immutable Auditability | Every transaction intent, policy result, risk score, XAI rationale, and execution result MUST be logged to append-only block-hashed tables. |
| **BR-010** | Universal Explainability | Every authorization decision (`ALLOW`, `REVIEW`, `BLOCK`) MUST be accompanied by feature attributions and a natural text explanation. |
| **BR-011** | Zero Credential Exposure | Raw bank account tokens, credit card numbers, or UPI PINs shall NEVER be exposed to AI agent models or LLM prompt contexts. |
| **BR-012** | Fail-Safe Security Default | System internal errors, timeouts, or component failures MUST default to `BLOCK` or `REVIEW`. Unverified `ALLOW` outputs are forbidden. |
| **BR-013** | User Ownership Isolation | Users can ONLY inspect, modify, or approve agents and transactions explicitly owned by their authenticated account. |
| **BR-014** | Atomic State Transitions | Payment intents and agents MUST exist in exactly one valid state at any time; invalid state transitions are forbidden. |
| **BR-015** | Idempotent Approval Lock | Real-time approval/rejection actions on pending intents MUST acquire distributed locks to prevent parallel duplicate execution. |
| **BR-016** | Positive Minor Unit Amounts| Transaction amounts MUST be positive integers in minor currency units (e.g. 250000 for ₹2,500.00); zero/negative values forbidden. |
| **BR-017** | Constant-Time Signature | HMAC signature comparison MUST execute using constant-time string algorithms to prevent side-channel timing attacks. |
| **BR-018** | 15-Minute Review TTL | Pending human approval requests unacted upon after 15 minutes MUST transition automatically to `EXPIRED` (rejected). |
| **BR-019** | Sub-100ms Gateway SLA | Total end-to-end intent processing latency (policy + fraud + XAI) MUST complete in $\le 100\text{ ms}$ at $p_{99}$. |
| **BR-020** | Zero Unconfigured Power | Unconfigured agent spending limits default to ZERO. Agents possess zero spending authority until policies are explicitly saved. |
| **BR-021** | MFA Required Governance | Modifying agent policies, executing key rotations, or disengaging Emergency Stop REQUIRES active MFA session verification. |
| **BR-022** | Dynamic Threshold Matrix| Financial limits and risk score thresholds MUST be loaded dynamically from configuration profiles; hardcoded thresholds forbidden. |
| **BR-023** | Adapter Decoupling | Payment execution logic MUST interface strictly via abstract Payment Adapters; hardcoding provider logic in core pipeline forbidden. |
| **BR-024** | Trace Reproducibility | XAI decision traces MUST record model artifact versions and feature vectors ensuring 100% historical audit reproducibility. |
| **BR-025** | Absolute Human Supremacy | Human account owner commands (Revocation, Emergency Stop, Rejection) ALWAYS override autonomous agent requests instantly. |
