# AGENTPAY — 37: Master Security Architecture Decision Records Index

## 1. Index Overview

This document indexes seventeen Security Architecture Decision Records (SEC-ADR-001 to SEC-ADR-017) located in `docs/architecture/phase-006-security-architecture/adrs/`.

---

## 2. SEC-ADR Summary Index

| ADR ID | Title | Security Objective | Decision Summary |
| :--- | :--- | :--- | :--- |
| **SEC-ADR-001**| Zero Trust Architecture | Continuous Verification | Enforce 9-step server-side validation on every request |
| **SEC-ADR-002**| Authentication Strategy | Strong Principal Identity | Argon2id passwords, TOTP MFA, HMAC-SHA256 for agents |
| **SEC-ADR-003**| Authorization Strategy | Least Privilege | Hybrid RBAC + ABAC with scoped capability tokens |
| **SEC-ADR-004**| Agent Identity | Principal Governance | Unique GUID identity keys with sub-10ms revocation |
| **SEC-ADR-005**| Agent Capability Security | Scope Isolation | Granular scopes (`spend:intent_create`, `cart:create`) |
| **SEC-ADR-006**| Payment Authorization | Replay Protection | Cryptographic Payment Authorization Context |
| **SEC-ADR-007**| Webhook Security | Signature Verification | Mandatory HMAC-SHA256 verification on all webhooks |
| **SEC-ADR-008**| Secrets Management | Zero Plaintext Secrets | HashiCorp Vault / KMS injection; zero secrets in Git |
| **SEC-ADR-009**| Encryption Strategy | Data Protection | TLS 1.3 in transit; AES-256-GCM at rest and field level |
| **SEC-ADR-010**| Tenant Isolation | Cross-Tenant Prevention | PostgreSQL Row-Level Security (RLS) + Redis namespaces |
| **SEC-ADR-011**| AI Security | Prompt Injection Defense | Strict prompt isolation + external policy gate supremacy |
| **SEC-ADR-012**| Tool Security | Tool Schema Validation | Mandatory JSON Schema validation and tool scope limits |
| **SEC-ADR-013**| Audit Security | Tamper Evidence | Immutable SHA-256 block hashing chain (`audit_logs`) |
| **SEC-ADR-014**| Admin Security | Privileged Access Control| Step-Up MFA authentication for administrative actions |
| **SEC-ADR-015**| Supply Chain Security | Vulnerability Prevention| Lockfile SHA pinning + Syft SBOM + Trivy container scans |
| **SEC-ADR-016**| Incident Response | Containment Protocols | Standardized P0-P3 response SLAs & automated playbooks |
| **SEC-ADR-017**| Emergency Kill Switch | Fail-Closed Emergency | Sub-100ms multi-tier emergency payment freeze |
