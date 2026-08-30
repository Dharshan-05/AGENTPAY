# AGENTGUARD Architecture Specification: Phase 214 — Decision Engine

## Overview
Phase 214 implements `AgentGuardDecisionService`, orchestrating all AGENTGUARD risk engines and policy evaluation.

## Decision Precedence
1. `DENIED`
2. `REQUIRE_APPROVAL`
3. `ALLOW` / `NO_APPLICABLE_POLICY`

## Guarantees
- Fail-closed security.
- Explicit policy `DENY` can NEVER be overridden by high trust scores or recommendation signals.
