# FRAUDGUARD ML Data Pipeline, Model Registry, Inference, Risk Intelligence, Explainable AI & REST API Specification (Phases 216–265)

## Overview
Phases 216–265 implement an enterprise-grade, deterministic, versioned, immutable, leakage-safe, tenant-isolated, real-time ML inference, risk intelligence, explainable AI (XAI) platform, and secure FastAPI REST endpoints integrated directly with the AGENTGUARD Risk Foundation (Phases 206–215).

```text
Raw Transaction / Agent Data
        ↓ (Phase 217 Dataset Integration)
Dataset Integration & Snapshots
        ↓ (Phase 218 Dataset Validation)
Dataset Validation & Quality Gate
        ↓ (Phase 219 Data Cleaning)
Data Cleaning & Quarantine
        ↓ (Phase 220 Data Preprocessing)
Data Preprocessing & State Management (Fitted PreprocessorState)
        ↓ (Phases 221-228 Feature Engineering)
Core, Transaction, Behaviour, Merchant, Velocity, Intent, Policy & Trust Risk Features
        ↓ (Phase 229 Feature Validation)
Feature Quality Gate
        ↓ (Phase 230 Feature Store)
Feature Store & Lineage Management
        ↓ (Phases 231-235 Training & Optimization)
Training Data Foundation, XGBoost Training & Hyperparameter Optimization
        ↓ (Phases 236-242 Model Evaluation Framework)
Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix Evaluators
        ↓ (Phases 243-245 Serialization, Versioning & Registry)
SHA-256 Native JSON Serialization, SemVer State Machine, PRODUCTION Model Registry
        ↓ (Phases 246-248 Real-Time Inference Engine)
PRODUCTION Model Resolution, Point-in-Time Correctness & Frozen Preprocessor Scaling
        ↓ (Phases 249-251 Probability, Transaction & Behaviour Risk Services)
Probability Validation [0,1], Transaction Risk [0,100], Upstream Behaviour Signal Integration
        ↓ (Phases 252-255 Merchant, Velocity, Intent & Policy Risk Intelligence)
Governed Risk Intelligence Services & Authoritative Policy DENY Precedence
        ↓ (Phases 256-260 FRAUDGUARD EXPLAINABLE AI - XAI)
SHAP Integration, Feature Importance, Local/Global XAI & Risk Factor Extraction
        ↓ (Phases 261-265 FRAUDGUARD FASTAPI REST CONTROLLER & E2E ORCHESTRATION)
┌──────────────────────────────────────────────────────────────────┐
│ FRAUDGUARD FASTAPI REST CONTROLLER & END-TO-END ORCHESTRATION    │
│ - Phase 261: XAI Explanation API (/fraudguard/xai/*)             │
│ - Phase 262: Explanation Response Contract & Risk Factor API     │
│ - Phase 263: Real-Time FraudGuard Inference API                  │
│ - Phase 264: FraudGuard Risk Intelligence API                    │
│ - Phase 265: End-to-End FraudGuard Integration (/evaluate)       │
└──────────────────────────────────────────────────────────────────┘
```

## Architectural & Security Guarantees
1. **Advisory Risk Signals & Strict Policy Precedence**: SHAP, ML predictions, and XAI explanations are strictly ADVISORY. ML models MUST NOT authorize transactions or override an explicit `POLICY DENY` or `AGENTGUARD DENY`. `FraudGuardApplicationService` enforces `allow_ml_scoring = False` when policy decision is `DENY`, and `UNKNOWN` policy decisions fail closed (`ValueError`).
2. **Probability vs Risk Score Unit Separation**: `fraud_probability` is strictly bounded to $[0.0, 1.0]$. Transaction, Merchant, Velocity, Intent, and Policy risk scores are strictly bounded to $[0.0, 100.0]$. Confidence is strictly $[0.0, 1.0]$. Unit mismatches fail closed.
3. **Data Leakage & Prohibited Target Features**: XAI endpoints explicitly reject target variables and post-outcome fields (`is_fraud`, `fraud_label`, `post_outcome`, `investigation_result`, `chargeback_result`, `future_outcome`).
4. **Point-in-Time & Temporal Safety**: Enforces `signal_timestamp <= prediction_timestamp` across all transaction explanations to prevent future data leakage.
5. **Production Model Binding & Checksum Verification**: Every inference or explanation request verifies the model lifecycle state (`PRODUCTION` for local inference) and verifies the SHA-256 artifact checksum before deserialization and execution.
6. **Multi-Tenant & Agent Isolation**: Tenant boundaries (`tenant_id`) and agent boundaries (`agent_id`) are strictly enforced across all FraudGuard API routes. Cross-tenant model access or data access fails closed with anti-enumeration protection.
7. **RBAC Permission Enforcement**: All FraudGuard REST endpoints enforce explicit RBAC permissions (`fraudguard:infer`, `fraudguard:risk_read`, `fraudguard:xai_read`, `fraudguard:evaluate`).
