# AGENTPAY — Functional Test Scenarios Specification

## 1. Overview

This document specifies 20 functional test scenarios (`FT-001` through `FT-020`) defining test goals, setup requirements, input vectors, expected outputs, state verification checks, and audit log validation rules.

---

## 2. Test Scenario Inventory

| Test ID | Title | Domain | Test Type | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **FT-001** | Successful Agent Registration | Agent Lifecycle | Positive | Agent created; HMAC secret issued ONCE; state `REGISTERED`. |
| **FT-002** | Invalid HMAC Signature Rejection | Authentication | Security / Negative | HTTP 401 `ERR_INVALID_SIGNATURE`; request blocked at edge. |
| **FT-003** | Revoked Agent Intent Attempt | Authentication | Security / Negative | HTTP 403 `ERR_AGENT_REVOKED`; zero processing overhead. |
| **FT-004** | Compliant Auto-Approved Purchase | Payment Pipeline | Positive | Intent passes policy/risk; state `EXECUTED` in < 100ms. |
| **FT-005** | Single Transaction Limit Breach | AGENTGUARD | Boundary / Negative| Decision `BLOCK`; reason `ERR_SINGLE_LIMIT_EXCEEDED`. |
| **FT-006** | Blocked Category MCC Violation | AGENTGUARD | Security / Negative| Decision `BLOCK`; reason `ERR_CATEGORY_BLOCKED`. |
| **FT-007** | Low-Risk Intent Auto-Approval | FRAUDGUARD | Positive | Score 12/100 (`LOW_RISK`); decision `ALLOW`. |
| **FT-008** | High-Value Intent Escalation | Approval Center | Boundary / Positive| Decision `REVIEW`; state `PENDING_APPROVAL`; Push alert sent.|
| **FT-009** | High-Risk Transaction Block | FRAUDGUARD | Security / Negative| Score 78/100 (`HIGH_RISK`); decision `BLOCK`. |
| **FT-010** | Critical-Risk Auto-Suspension | Security / Alerts | Security / Negative| Score 94/100 (`CRITICAL_RISK`); `BLOCK` + Agent state `SUSPENDED`.|
| **FT-011** | Human Single-Click Approval | Approval Center | Positive | User clicks Approve; state `AUTHORIZED` $\rightarrow$ `EXECUTED`. |
| **FT-012** | Human Approval Rejection | Approval Center | Negative | User clicks Reject; state `REJECTED`. |
| **FT-013** | Approval 15-Min TTL Expiration | Approval Center | Boundary / Negative| Unacted intent after 15m transitions to `EXPIRED`. |
| **FT-014** | Duplicate Idempotency Key | Payment Intent | Boundary / Positive| Second request receives cached HTTP 200 OK without re-evaluating. |
| **FT-015** | Gateway Timeout Failure | Payment Exec | Network / Fail-Safe| Gateway times out (5s); state `FAILED (ERR_GATEWAY_TIMEOUT)`.|
| **FT-016** | ML Model Failure Fallback | AI/ML Safety | Fail-Safe | ML timeout; falls back to rules; min `MEDIUM_RISK` assigned.|
| **FT-017** | XAI Summary Text Verification | XAI Engine | Accuracy | Natural text summary contains correct amount, limit, and MCC text.|
| **FT-018** | Global Emergency Stop Switch | Emergency Ctrl | Security / Stress | User clicks Kill Switch; all agents `SUSPENDED` in < 100ms. |
| **FT-019** | Immutable Audit Block Hash | Audit Trail | Security / Integrity| DB audit entries form valid SHA-256 block hash chain. |
| **FT-020** | Parallel Double-Spend Attempt | Concurrency | Stress / Security | Parallel requests with same key; exactly ONE executes. |
