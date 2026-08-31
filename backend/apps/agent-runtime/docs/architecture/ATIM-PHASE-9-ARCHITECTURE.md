# AGENTPAY — ATIM Phase 9 Architecture: Intelligent Model Routing & Adaptive Inference

## Overview
Phase 9 introduces deterministic, risk-aware model routing and adaptive inference for AGENTPAY transactions.

---

## Routing Flow

```text
                    USER REQUEST
                         │
                         ▼
                 ATIM SECURITY (Phase 4)
                         │
                         ▼
                 TASK CLASSIFIER
                         │
                         ▼
                 RISK CLASSIFIER
                         │
                         ▼
              MODEL ELIGIBILITY FILTER
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       MODEL REGISTRY          PROVIDER HEALTH
             │                       │
             └───────────┬───────────┘
                         ▼
                  ROUTING ENGINE
                         │
                         ▼
                 SELECTED MODEL
                         │
                         ▼
                  LLM PROVIDER
                         │
                         ▼
              STRUCTURED OUTPUT
                         │
                         ▼
                ATIM VALIDATION
                         │
                         ▼
               PLAN VALIDATION
                         │
                         ▼
                  AGENTGUARD
                         │
                         ▼
                  FRAUDGUARD
                         │
                         ▼
                      HITL
                         │
                         ▼
                    RAZORPAY
```

---

## Provider Circuit Breaker State Machine
- **CLOSED**: Provider operational, normal routing enabled.
- **OPEN**: Provider experienced $\ge 3$ consecutive failures. Requests immediately fail over.
- **HALF_OPEN**: Cooldown period (60s) expired; single probe request allowed to verify recovery.

---

## Invariant Guards
1. **User/LLM Input Cannot Control Routing**: Model selection is strictly server-side.
2. **Security Floor Enforcement**: Unsafe models are strictly filtered out before scoring.
3. **Fail-Closed Fallback Cascade**: Primary model $\rightarrow$ Secondary model $\rightarrow$ Rule engine fallback $\rightarrow$ Reject.
