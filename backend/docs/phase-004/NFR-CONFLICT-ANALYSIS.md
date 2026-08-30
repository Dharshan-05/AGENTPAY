# AGENTPAY — NFR Conflict Analysis & Resolution

## 1. Overview

This document formalizes the resolution principles governing trade-off conflicts between competing quality attributes (e.g. Security vs Performance, Availability vs Fail-Closed Security, Latency vs XAI depth).

---

## 2. NFR Conflict Resolution Catalog

### Conflict 1: Security vs Performance
* **Tension**: Cryptographic HMAC signature verification, Argon2id hashing, and multi-stage policy rules add CPU overhead, conflicting with machine-speed 100ms latency targets.
* **Governing Principle**: **"Financial Safety > Performance Optimization."**
* **Resolution**: Security checks are non-negotiable. Performance SLAs are met by caching verified policy profiles and active key states in Redis edge instances ($< 2\text{ ms}$ lookup), maintaining total pipeline execution $\le 100\text{ ms}$ without relaxing security validation.

### Conflict 2: Availability vs Fail-Closed Security
* **Tension**: Maintaining high service availability ($99.9\%$) conflicts with strict fail-closed security default principles (`NFR-RESL-001`) under internal component outages.
* **Governing Principle**: **"Fail-Closed Security > Availability."**
* **Resolution**: If an internal datastore or ML scoring container crashes, AGENTPAY explicitly chooses to reject/escalate incoming payment intents rather than bypassing security gates to maintain fake availability. Unverified `ALLOW` decisions are strictly forbidden.

### Conflict 3: Latency vs XAI Explanation Depth
* **Tension**: Complex deep learning explainability models (e.g. real-time SHAP tree evaluation) can take $> 200\text{ ms}$, breaching the 100ms end-to-end SLA.
* **Governing Principle**: **"Pre-compute feature weight vectors during inference scoring."**
* **Resolution**: FRAUDGUARD calculates feature weights during the primary forward scoring pass, allowing the XAI Engine to synthesize explanations using template injection in $< 10\text{ ms}$.

### Conflict 4: Scalability vs Strict Financial Consistency
* **Tension**: High horizontal scaling throughput relies on eventual consistency, whereas financial daily spending caps require strict ACID consistency.
* **Governing Principle**: **"Financial Integrity > Horizontal Throughput."**
* **Resolution**: Budget checking and updating execute under atomic Redis `INCRBY` commands or PostgreSQL row-level locks (`SELECT FOR UPDATE`), guaranteeing zero double-spending or budget overruns even under high concurrent load.
