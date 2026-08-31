# ATIM Group 6 — Model Governance & Adaptive Routing Policy

## 1. Policy Overview
This document specifies the authoritative governance rules, security floor gates, adaptive scoring weights, budget quota policies, and fallback cascades enforced across ATIM Group 6 (Phases 11 & 12).

---

## 2. Hard Security Floor Policy
- **Minimum Threshold**: `ATIM_SECURITY_MIN_SCORE = 0.95`.
- **Enforcement Level**: Pre-routing eligibility gate.
- **Rule**: If a model profile or version has a security score $< 0.95$, it is immediately classified as `INELIGIBLE` for production routing regardless of latency, reasoning capabilities, or cost.

---

## 3. Cost Budget Quota Policy
- **Budget Levels**:
  - `max_cost_per_request`: Max USD cost per single inference request (Default: `$0.050000`).
  - `daily_budget_usd`: Daily tenant budget limit (Default: `$50.000000`).
  - `monthly_budget_usd`: Monthly tenant budget limit (Default: `$1000.000000`).
- **Enforcement**: If a candidate model's estimated cost would breach any budget limit, it is marked `INELIGIBLE_BUDGET_EXCEEDED`, and the router falls back to a cheaper eligible model.
- **Fail Closed**: If no safe, eligible model fits within the budget, execution fails closed (`DENY`).

---

## 4. Adaptive Scoring Formula
The deterministic routing score for an eligible model $m$ on task $t$ is calculated as:

$$\text{Score}(m, t) = w_q \cdot Q(m, t) + w_s \cdot S(m) + w_r \cdot R(m) + w_l \cdot L(m) + w_c \cdot C(m)$$

Where:
- $Q(m, t)$: Task-specific historical quality score $\in [0, 1]$
- $S(m)$: Security score $\in [0.95, 1.0]$
- $R(m)$: Provider reliability score $(1 - \text{error\_rate}) \in [0, 1]$
- $L(m)$: Normalized latency score $\in [0, 1]$
- $C(m)$: Cost efficiency score $\in [0, 1]$
- Weights: $w_q = 0.35, w_s = 0.25, w_r = 0.20, w_l = 0.10, w_c = 0.10$

---

## 5. Governance State Transitions & Authorization
| Current Status | Target Status | Required Authorization / Event |
|---|---|---|
| `CANDIDATE` | `EVALUATING` | Triggered by benchmark runner |
| `EVALUATING` | `APPROVED` | All evaluation & regression gates PASS |
| `EVALUATING` | `REJECTED` | Any security or regression gate FAILS |
| `APPROVED` | `CHAMPION` | Server-side RBAC authorization (`atim:model:approve`) |
| `CHAMPION` | `ROLLED_BACK` | Manual rollback or automatic SLO regression trigger |
