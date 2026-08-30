# AGENTPAY — Disaster Recovery Non-Functional Requirements

## 1. Overview

Disaster Recovery requirements specify automated recovery procedures, cache rebuild protocols, failover behavior, and data reconstruction strategies across major component outage scenarios.

---

## 2. Requirement Baseline

### NFR-DR-001: Automatic Redis Cache Reconstruction Protocol
* **NFR ID**: `NFR-DR-001`
* **Title**: Automatic Redis Edge Policy Cache Reconstruction Protocol
* **Source FR**: `FR-AGD-001`, `FR-ERR-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Disaster Recovery
* **Requirement**: If the Redis cache container crashes or loses state, application workers shall automatically fall back to querying policy rules directly from PostgreSQL and asynchronously rebuild the Redis edge cache within $< 60\text{ seconds}$.
* **Rationale**: Ensures continuous, resilient policy enforcement even during total cache layer failure.
* **Metric & Target**: Cache rebuild completed in $< 60\text{ seconds}$; zero dropped intents during rebuild.
* **Measurement Method**: Fault injection executing `redis-cli FLUSHALL` under active transaction load.
* **Acceptance Criteria**: Intent evaluation degrades gracefully to DB query mode; cache completely repopulated in $< 60\text{ seconds}$.
* **Dependencies**: PostgreSQL primary datastore.
