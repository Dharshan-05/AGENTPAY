# ATIM Group 10 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes industry standards in API security hardening, Zero Trust authorization, cryptographic compliance evidence, and SOC 2 Type II forensic auditability to inform **ATIM Group 10 (Phases 19 & 20)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE with ZERO FINANCIAL AUTHORITY**.
- **All administrative, governance, diagnostic, and execution APIs MUST enforce server-side RBAC and strict tenant/agent isolation prior to LLM or database execution**.
- **Cryptographic compliance evidence records MUST be immutable, append-only, and signed with SHA-256 HMAC**.

---

## Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **NIST SP 800-207 Zero Trust / OWASP API Security** | Pre-execution authorization, fine-grained RBAC permissions (`ATIM_POLICY_READ`, `ATIM_POLICY_APPROVE`), server-resolved tenant identity, fail-closed enforcement. | Implement `ATIMAuthorizationService` validating principal identity, permissions, and tenant/agent ownership server-side. | **ADAPT** | Adopt pre-execution RBAC & tenant scoping; REJECT trusting client-supplied or LLM-generated tenant/agent IDs. |
| **SOC 2 Type II / Sigstore / Forensic Audit Logging** | Tamper-proof append-only compliance evidence, SHA-256 HMAC cryptographic signatures, canonical payload hashing, decision precedence tracking. | Implement `ATIMComplianceEvidenceService` generating immutable forensic evidence records with HMAC signatures. | **ADAPT** | Adopt immutable audit signing; REJECT mutable or un-signed audit records. |
| **CIS Benchmarks / NIST SP 800-53** | Automated compliance verification, fail-closed dependency checks, fail-closed readiness scorecards. | Integrate compliance evidence verification into `ATIMSystemAuditService` scorecard. | **ADAPT** | Adopt automated compliance audit scorecard; REJECT claiming production readiness when any security control fails. |

---

## Detailed Pattern Decisions

### 1. Enterprise API Security & Authorization Hardening (Phase 19)
- **ADAPT**: Centralized RBAC permission check (`ATIMAuthorizationService`) enforcing `ATIM_POLICY_READ`, `ATIM_POLICY_CREATE`, `ATIM_POLICY_SUBMIT`, `ATIM_POLICY_APPROVE`, `ATIM_POLICY_ACTIVATE`, `ATIM_POLICY_SUSPEND`, `ATIM_POLICY_RETIRE`, `ATIM_POLICY_AUDIT`, `ATIM_SYSTEM_ADMIN`. Enforce server-side tenant isolation (`authenticated_tenant == target_tenant`).
- **REJECT**: Allowing unauthenticated or cross-tenant access to governance, telemetry, or threat intelligence APIs.

### 2. Compliance Evidence & Forensic Auditability (Phase 20)
- **ADAPT**: Cryptographic compliance evidence engine (`ATIMComplianceEvidenceService`) recording append-only audit evidence with HMAC-SHA256 signatures for authentication failures, authorization denials, governance transitions, rate limit violations, security blocks, and financial proposals.
- **REJECT**: Overwriting or deleting historical compliance evidence records.
