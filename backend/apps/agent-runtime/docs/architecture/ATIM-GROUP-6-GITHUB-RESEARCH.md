# ATIM Group 6 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes open-source AI agent, evaluation, routing, and guardrail frameworks to inform the architectural enhancement of the **AgentPay Transaction Intelligence Model (ATIM) Group 6 (Phases 11 & 12)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE**.
- **Server-side deterministic security controls retain 100% financial authority**.
- **No external dependency is introduced unless explicitly justified**.

---

## Comparative Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **OpenAI Evals / Agents SDK** | Continuous benchmark evaluations, dataset versioning, eval harness | Immutable dataset versioning (`DatasetVersion`), `EvaluationRun` tracking, versioned prompt/model metrics | **ADAPT** | Adopt benchmark runner structure; REJECT auto-tuning LLM self-evaluations. |
| **Instructor** | Pydantic schema enforcement, structured output validation | Schema validation failure rate metric, deterministic structural compliance scoring | **ADAPT** | Adopt schema failure rate telemetry; preserve strict Pydantic parsing. |
| **LiteLLM** | Multi-provider routing, fallback cascades, cost/token tracking | Tenant/Agent cost budget quotas (`CostBudget`), cost-efficiency routing weights, provider circuit breakers | **ADAPT** | Adopt cost accounting & fallback cascades; REJECT unconstrained auto-switching that bypasses security floors. |
| **Guardrails AI / NeMo** | Programmable security rails, input/output guardrails | Hard security floor gate (`security_score >= configured_floor`) enforced *before* model scoring | **ADAPT** | Enforce security floor as a hard eligibility gate. Security score cannot be traded off for lower cost/latency. |
| **DeepEval / promptfoo** | Regression detection, prompt testing, evaluation scorecards | Composite Governance Score calculator, regression tolerance checks, Champion/Challenger deployment gates | **ADAPT** | Adopt deterministic regression tolerance checks (`PASS/WARN/FAIL`) and Champion/Challenger governance flow. |
| **LangSmith / MLflow** | Observability, evaluation tracking, model governance registries | Immutable governance audit logs (`atim_governance_decisions`), deployment state machine (`CANDIDATE` to `APPROVED`/`REJECTED`) | **ADAPT** | Adopt model versioning and audit trail; REJECT external cloud logging of raw prompts/secrets. |

---

## Detailed Pattern Decisions

### 1. Model & Prompt Governance (Phase 11)
- **REUSE**: Phase 8 evaluation scorecard builder (`ATIMModelScorecardBuilder`) and Phase 9 Model Registry (`ATIMModelRegistry`).
- **ADAPT**: Create immutable governance entities (`ModelVersion`, `PromptVersion`, `DatasetVersion`, `EvaluationRun`, `GovernanceDecision`).
- **REJECT**: External cloud evaluation dependencies or LLM self-promotion. Promotion requires explicit server-side RBAC authorization (`atim:model:approve`).

### 2. Regression Engine & Deployment Gates (Phase 11)
- **REUSE**: `ATIMRegressionEngine` from Phase 8.
- **ADAPT**: Extend regression checks to evaluate accuracy, security, latency, and cost tolerances against baseline Champion scorecards.
- **REJECT**: Automatic promotion upon evaluation completion without server-side governance approval.

### 3. Adaptive & Cost-Aware Routing (Phase 12)
- **REUSE**: `ATIMIntelligentRouter` and `ATIMCircuitBreaker` from Phase 9.
- **ADAPT**: Integrate Exponentially Weighted Moving Averages (EWMA) for historical telemetry, task-specific performance matrix, tenant/agent cost budget quotas (`TenantLLMQuota`), and routing decision explanation objects.
- **REJECT**: Reinforcement learning or online LLM prompt self-modification. Adaptive routing remains 100% deterministic given the same state, policies, and telemetry.
