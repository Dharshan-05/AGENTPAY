# ATIM Phase 11 Architecture — Continuous LLM Evaluation, Regression & Model Governance

## Executive Summary
**ATIM Phase 11** implements a production-grade governance and evaluation layer for the **AgentPay Transaction Intelligence Model (ATIM)** infrastructure.

Phase 11 introduces:
1. **Immutable Versioning**: Immutably versions LLM models (`ModelVersion`), prompt templates (`PromptVersion`), and benchmark datasets (`DatasetVersion`).
2. **Deterministic Composite Governance Score**: Combines Accuracy, Security, Reliability, Performance, and Cost scores.
3. **Hard Security Floor Gate**: Enforces that models with `security_score < configured_security_floor` (default: 0.95) are marked `INELIGIBLE` regardless of speed or cost.
4. **Regression Engine**: Compares candidate models against active Champion baselines with configurable degradation tolerances.
5. **Champion / Challenger Governance Flow**: Evaluates Challengers against Champions without auto-promotion. Promotion requires explicit server-side RBAC authorization (`atim:model:approve`).
6. **Canary Routing & Controlled Rollbacks**: Enables controlled traffic split for approved Challengers with deterministic single-step rollback to `last_known_good_model`.

---

## Model Governance State Machine

```text
               ┌────────────────────────┐
               │       CANDIDATE        │
               └───────────┬────────────┘
                           │ Run Evaluation
                           ▼
               ┌────────────────────────┐
               │       EVALUATING       │
               └─────┬────────────┬─────┘
  Security /         │            │  Passes Security &
  Regression Fail    │            │  Regression Benchmarks
                     ▼            ▼
         ┌──────────────┐      ┌──────────────┐
         │   REJECTED   │      │   APPROVED   │
         └──────────────┘      └──────┬───────┘
                                      │ Admin Authorization
                                      │ (atim:model:approve)
                                      ▼
                               ┌──────────────┐
                               │   CHAMPION   │
                               └──────┬───────┘
                                      │ Instability / Degradation
                                      ▼
                               ┌──────────────┐
                               │  ROLLED_BACK │
                               └──────────────┘
```

---

## Key Invariants
- **No Self-Promotion**: LLMs cannot approve their own promotion or alter governance policies.
- **Hard Security Floor**: Any model failing `security_score >= 0.95` is rejected.
- **Auditability**: Every status transition generates an immutable governance audit record (`atim_governance_decisions`).
