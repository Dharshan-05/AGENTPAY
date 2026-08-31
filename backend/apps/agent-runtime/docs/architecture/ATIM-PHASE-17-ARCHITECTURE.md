# ATIM Phase 17 Architecture — Governance, Policy Lifecycle & Administrative Control Plane

## Executive Summary
**ATIM Phase 17** implements an administrative governance control plane for policy lifecycle management in **AgentPay Transaction Intelligence Model (ATIM)**.

Phase 17 features:
1. **Policy Lifecycle State Machine (`GovernancePolicyStatus`)**: Strongly typed state machine enforcing `DRAFT` $\rightarrow$ `PENDING_APPROVAL` $\rightarrow$ `APPROVED` $\rightarrow$ `ACTIVE` $\rightarrow$ `SUSPENDED` $\rightarrow$ `RETIRED`. Invalid state transitions are rejected.
2. **Strongly Typed Policy Categories (`GovernancePolicyType`)**: `ATIM_SECURITY_POLICY`, `ATIM_MODEL_ROUTING_POLICY`, `ATIM_RISK_POLICY`, `ATIM_RATE_LIMIT_POLICY`, `ATIM_QUOTA_POLICY`, `ATIM_PROVIDER_POLICY`.
3. **Four-Eyes Principle (`creator != approver`)**: Enforces separation of duties for security-sensitive policy approvals. The creator of a draft policy cannot approve their own submission.
4. **Policy Version Immutability**: Active policies are never overwritten. Every modification creates a new immutable version (`v1`, `v2`, `v3`).
5. **Cryptographic Audit Signature Integration**: Integrates with `ATIMAuditLockService` to sign every policy lifecycle event with HMAC-SHA256 signatures.

---

## Policy Lifecycle State Machine

```text
       ┌────────┐
       │ DRAFT  │
       └───┬────┘
           │ (Submit)
           ▼
┌──────────────────┐
│ PENDING_APPROVAL │
└──────────┬───────┘
           │ (Approve - creator != approver)
           ▼
      ┌──────────┐
      │ APPROVED │
      └────┬─────┘
           │ (Activate)
           ▼
       ┌────────┐ (Suspend)  ┌───────────┐
       │ ACTIVE │───────────►│ SUSPENDED │
       └───┬────┘◄───────────└─────┬─────┘
           │ (Retire)              │ (Retire)
           ▼                       ▼
      ┌─────────┐             ┌─────────┐
      │ RETIRED │             │ RETIRED │
      └─────────┘             └─────────┘
```
