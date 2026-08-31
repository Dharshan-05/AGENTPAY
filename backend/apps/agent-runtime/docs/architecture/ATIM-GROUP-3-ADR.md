# AGENTPAY — Architectural Decision Record (ADR): ATIM Group 3

## Status
**APPROVED & IMPLEMENTED**

## Context
AGENTPAY requires a natural-language transaction intelligence layer (ATIM) that enables AI agents to understand commercial requests, query memory, and generate proposed execution plans. However, in financial systems, LLMs must NEVER become authorization authorities or execute money movement directly.

## Decisions

### 1. ATIM as Untrusted Proposal Layer
ATIM is strictly an untrusted intelligence and proposal engine. The LLM cannot authorize payments, alter AGENTGUARD policies, modify spending limits, override RBAC, bypass HITL, or directly execute financial tools.

### 2. AGENTGUARD Authoritative Policy Engine
Server-side `AgentGuardDecisionService` remains the sole authority for policy evaluation, spending limit enforcement, scope checks, velocity rules, and trust score calculations.

### 3. FRAUDGUARD Authoritative ML Engine
Server-side `FraudGuardApplicationService` remains the sole authority for real-time XGBoost fraud probability scoring, risk classification, and SHAP XAI explanations.

### 4. Deterministic Precedence Decision Engine
Final transaction execution decisions follow a strict deterministic precedence order:
$$\text{SECURITY BLOCK} \rightarrow \text{PLAN INVALID} \rightarrow \text{AGENTGUARD DENY} \rightarrow \text{FRAUDGUARD BLOCK} \rightarrow \text{HITL REQUIRED} \rightarrow \text{ALLOW}$$
LLM confidence scores or prompt instructions cannot override security or fraud rejections.

### 5. Server-Controlled Human-in-the-Loop (HITL)
Server-side rules determine whether human approval is required based on transaction amount, risk level, policy requirements, or new merchants. LLM confidence output cannot bypass HITL requirements.

### 6. Strict Decimal Financial Arithmetic
All financial values are parsed into `Decimal` instances with strict ISO 4217 currency validation. Floating-point arithmetic, NaN, Infinity, negative values, or LLM-defined exchange rates are strictly rejected.

### 7. Feature Provenance Integrity
Fraud features passed to FRAUDGUARD carry explicit provenance metadata (`USER-PROVIDED`, `AGENT-PROVIDED`, `DATABASE`, `TRANSACTION`, `DEVICE`, `BEHAVIORAL`, `MERCHANT`, `SYSTEM`). Untrusted LLM values cannot silently become trusted fraud features.

### 8. Hardened Tool Execution Boundary
ATIM can only propose tool invocations. Tool execution requires Tool Registry schema validation, RBAC evaluation, AGENTGUARD evaluation, FRAUDGUARD evaluation, and HITL approval.

### 9. Tenant & Agent Memory Isolation
All memory queries strictly enforce `tenant_id` + `agent_id` filtering at the SQL query layer. Malicious memory records are quarantined (`score = 0.0`) and excluded from prompt context.
