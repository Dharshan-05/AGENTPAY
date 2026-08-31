# AGENTPAY — ATIM Phase 9 Routing Policy & Configuration Specification

## Overview
This document specifies the deterministic model routing policy rules, risk classification thresholds, and circuit breaker governance for AGENTPAY.

---

## Routing Policy Rules

### 1. Hard Security Floor Rule
No request shall be routed to an LLM provider model with a `security_score < 0.95` or `schema_score < 0.95`.

### 2. Risk-Weighted Model Scoring
$$\text{Score} = w_{\text{sec}} \cdot S_{\text{security}} + w_{\text{acc}} \cdot S_{\text{accuracy}} + w_{\text{cost}} \cdot S_{\text{cost}}$$
- **High/Critical Financial Risk**: $w_{\text{sec}} = 0.60, w_{\text{acc}} = 0.30, w_{\text{cost}} = 0.10$
- **Low Risk Operations**: $w_{\text{sec}} = 0.30, w_{\text{acc}} = 0.40, w_{\text{cost}} = 0.30$

### 3. Fallback Order
$$\text{Primary Model} \rightarrow \text{Secondary Model} \rightarrow \text{Rule-Engine Fallback} \rightarrow \text{Fail Closed}$$

### 4. Circuit Breaker Parameters
- **Failure Threshold**: 3 consecutive failures
- **Cooldown Duration**: 60 seconds
- **Probe Policy**: 1 request allowed in `HALF_OPEN` state
