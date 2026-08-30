# AGENTPAY — Auditability Non-Functional Requirements

## 1. Overview

Auditability requirements define audit log retention periods, tamper-evident cryptographic verification standards, and audit trail query SLAs.

---

## 2. Requirement Baseline

### NFR-AUD-001: Immutable Audit Block Hash Chain Verification
* **NFR ID**: `NFR-AUD-001`
* **Title**: Tamper-Evident SHA-256 Block Chain Audit Verification SLA
* **Source FR**: `FR-AUD-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Auditability
* **Requirement**: $100.0\%$ of audit trail events shall be linked via SHA-256 block hash chains. Database permissions shall deny `UPDATE` and `DELETE` queries on audit tables.
* **Rationale**: Ensures compliance proof and tamper evidence for financial regulatory audits.
* **Metric & Target**: $100.0\%$ Cryptographic Verification; $0$ un-hashed audit records.
* **Measurement Method**: Daily automated cryptographic verification script.
* **Acceptance Criteria**: Verifier confirms valid hash chain over 100,000 audit log records.
* **Dependencies**: `FR-AUD-001`.
