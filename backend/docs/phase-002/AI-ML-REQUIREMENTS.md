# AGENTPAY — AI/ML Requirements

## 1. Overview

This document specifies the operational, structural, governance, and fail-safe requirements for machine learning models and statistical classifiers powering **FRAUDGUARD**.

---

## 2. Requirement Baseline

### 2.1 Model Governance & Metadata Tracking
* **REQ-AML-001**: Every deployed ML model artifact shall record immutable metadata including `model_version`, `training_timestamp`, `feature_schema_version`, and `performance_metrics` (ROC-AUC, Precision, Recall).
* **REQ-AML-002**: The inference pipeline shall log the exact `model_version` used for every transaction evaluation to ensure 100% reproducible decision tracing.

### 2.2 Inference Pipeline & Feature Inputs
* **REQ-AML-003**: The ML inference service shall ingest a standardized 12-dimensional feature vector derived from real-time Redis counters and historical database tables.
* **REQ-AML-004**: Missing feature values shall be handled using explicit imputers (e.g. median substitution for numerical values, missing category tags for categorical variables).

### 2.3 Model Performance & Monitoring
* **REQ-AML-005**: The system shall monitor model prediction drift and feature distribution shifts in real-time.
* **REQ-AML-006**: Model inference latency shall not exceed $30\text{ ms}$ at $p_{99}$.

### 2.4 Fail-Safe Strategy on AI Model Failure
* **REQ-AML-007**: If the ML inference service experiences a timeout, crash, or memory exception, the system shall execute an automatic fail-safe fallback:
  $$\text{AI Model Failure} \longrightarrow \text{Fallback to Deterministic Rule Engine} \longrightarrow \text{Assign Min } \text{MEDIUM\_RISK}$$
* **REQ-AML-008**: In the event of AI model failure, the system shall NEVER automatically default to `ALLOW`. All fallback decisions must require human review or enforce strict policy limits.
