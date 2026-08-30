# AGENTPAY — Audit Trail Functional Specifications

## 1. Overview

Audit Trail functions specify immutable append-only logging, SHA-256 cryptographic block hashing chain generation, and audit trail query interfaces.

---

## 2. Specifications

### FR-AUD-001: Append-Only Block Hash Audit Logging
* **FR ID**: `FR-AUD-001`
* **Title**: Append-Only Immutable Audit Log Creation & Cryptographic Block Hashing
* **Source**: `REQ-AUD-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Audit Service (`SYSTEM`)
* **Goal**: Record immutable, tamper-evident audit entries for every transaction decision and system state change.
* **Preconditions**: Auditable event emitted (`PAYMENT_EXECUTED`, `POLICY_EVALUATED`, `AGENT_REVOKED`).
* **Trigger**: Pipeline step completion.
* **Inputs**: `event_type`, `actor`, `target_entity_id`, `payload_json`, `timestamp`.
* **Main Flow**:
  1. Audit Service fetches `previous_block_hash` from previous audit entry.
  2. Audit Service constructs current block string: `prev_hash:timestamp:event_type:actor:entity_id:payload_hash`.
  3. Audit Service computes current SHA-256 block hash:
     $$H_{\text{curr}} = \text{SHA256}(\text{BlockString})$$
  4. Audit Service writes entry to append-only database table (`audit_logs`) with $H_{\text{curr}}$.
* **Business Rules**: `BR-009`, `BR-010`.
* **Database Rules**: `UPDATE` and `DELETE` queries strictly blocked at database permissions layer.
* **Outputs**: Persisted Immutable Audit Entry object.
* **Audit Events**: Self-auditing append log write.
* **Acceptance Criteria**: `AC-AUD-001`.
* **Dependencies**: None.
