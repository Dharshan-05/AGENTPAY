# AGENTPAY — Backup & Restore Non-Functional Requirements

## 1. Overview

Backup & Restore requirements define Recovery Point Objectives (RPO), Recovery Time Objectives (RTO), database snapshot frequencies, and backup integrity verification rules.

---

## 2. Requirement Baseline

### NFR-BKP-001: Recovery Point Objective (RPO) & Recovery Time Objective (RTO)
* **NFR ID**: `NFR-BKP-001`
* **Title**: RPO $< 1\text{ Hour}$ and RTO $< 15\text{ Minutes}$ Target
* **Source FR**: `FR-AUD-001`
* **Priority**: P2 | **Target Horizon**: FUTURE PRODUCTION TARGET
* **Category**: Backup & Restore
* **Requirement**: Relational database snapshots and WAL transaction logs shall achieve an RPO of $< 1\text{ hour}$ (max 1 hour data loss on catastrophic loss) and an RTO of $< 15\text{ minutes}$ (full database restoration time).
* **Rationale**: Protects business transaction history against catastrophic cloud infrastructure failure.
* **Metric & Targets**: RPO $< 1\text{ hour}$; RTO $< 15\text{ minutes}$.
* **Measurement Method**: Quarterly automated database restore drill in staging environment.
* **Acceptance Criteria**: Database point-in-time restore completes in $< 15\text{ minutes}$ with data loss $< 1\text{ hour}$.
* **Dependencies**: Relational database WAL archiving.
