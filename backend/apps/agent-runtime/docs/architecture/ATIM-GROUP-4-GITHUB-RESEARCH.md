# AGENTPAY — ATIM Group 4 GitHub Reference Architecture Research

## Overview
This document records the architectural pattern research conducted for **ATIM Group 4** (Phase 8 Evaluation & Phase 9 Intelligent Routing) against open-source agentic, evaluation, and LLM routing frameworks.

---

## Pattern Analysis & Decisions

### 1. OpenAI Agents SDK (`openai/openai-agents-python`)
- **Patterns Studied**: Tracing spans, evaluation runner interfaces, model capability profiling, structured output validation hooks.
- **AGENTPAY Requirement**: Quantitative benchmarking of intent extraction, planning, and security defense.
- **Decision**: **ADAPT**
- **Rationale**: Adopt evaluation runner interfaces and structured scorecard tracking. Reject autonomous agent execution loops.
- **Security Impact**: Positive. Benchmarking runs natively in isolated evaluation suites without touching payment execution gates.
- **Dependency Impact**: Zero added dependencies.

### 2. Instructor (`567-labs/instructor`)
- **Patterns Studied**: Schema failure rate tracking, retry validation metrics, Pydantic model validation scorecards.
- **AGENTPAY Requirement**: Measure schema validity rates and validation failure rates per provider and model.
- **Decision**: **ADAPT**
- **Rationale**: Track schema failure rates and retry frequency in `ATIMEvaluationService` scorecards.
- **Security Impact**: Positive. Models with high schema failure rates (> 5%) are flagged `INELIGIBLE`.
- **Dependency Impact**: Zero added dependencies.

### 3. LiteLLM (`BerriAI/litellm`)
- **Patterns Studied**: Intelligent model routing, provider health tracking, circuit breaker failover, token cost tracking per request/provider.
- **AGENTPAY Requirement**: Dynamic policy-driven routing across OpenAI and Anthropic based on risk level, task type, latency, cost, and provider health.
- **Decision**: **ADAPT** (Native Implementation)
- **Rationale**: Adopt circuit breaker state machine (`CLOSED`, `OPEN`, `HALF_OPEN`), provider health tracking, and token cost tracking concepts. Implement natively without importing `litellm` package to keep attack surface minimal.
- **Security Impact**: Positive. Enforces administrator-controlled hard security floors.
- **Dependency Impact**: Zero added dependencies.

### 4. Guardrails AI (`guardrails-ai/guardrails`)
- **Patterns Studied**: Validator scoring pipelines, attack block rate metrics, security evaluation benchmarks.
- **AGENTPAY Requirement**: Benchmark prompt injection defense, secret redaction, and PII masking block rates.
- **Decision**: **ADAPT**
- **Rationale**: Implement `SecurityEvaluationResult` measuring attack detection rates and false positive rates on commercial terms.
- **Security Impact**: Positive. Models failing the 0.95 security floor are disqualified from financial routing.
- **Dependency Impact**: Zero added dependencies.

### 5. Microsoft AutoGen (`microsoft/autogen`)
- **Patterns Studied**: Multi-agent evaluation concepts and benchmark datasets.
- **AGENTPAY Requirement**: Benchmark single-agent transaction intelligence.
- **Decision**: **REJECT**
- **Rationale**: Reject multi-agent autonomous negotiation or routing frameworks. All routing in AGENTPAY is server-controlled and deterministic.
- **Security Impact**: Positive. Prevents multi-agent non-deterministic routing.
- **Dependency Impact**: Zero added dependencies.
