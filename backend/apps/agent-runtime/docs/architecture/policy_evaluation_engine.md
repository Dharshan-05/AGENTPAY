# AGENTGUARD Architecture Specification: Phase 187 — Policy Evaluation Engine

## Overview
Phase 187 implements `PolicyEvaluationService`, building the central deterministic policy evaluation engine for AGENTGUARD.

## Evaluation Pipeline & Decision Semantics
1. **Agent Identity Verification**: Integrates `AgentIdentityVerificationService`. If agent identity is unverified or inactive, returns `decision = "DENIED"`, `reason_codes = ["IDENTITY_NOT_VERIFIED"]`.
2. **Active Policy Resolution**: Fetches policies for `tenant_id` where `status == "active"`, `deleted_at.is_(None)`, and current time is within `[starts_at, ends_at]`.
3. **Deterministic Ordering**: Sorts policies by `priority DESC, id ASC`.
4. **Conflict Resolution Precedence**:
   - `DENY` > `REQUIRE_APPROVAL` > `ALLOW`.
   - Any policy with `enforcement_mode == "block"` or threshold breach causes `DENIED`.
   - Any policy with `enforcement_mode == "warn"` or threshold warning causes `REQUIRE_APPROVAL`.
   - If no active policies exist in tenant scope, returns `NO_APPLICABLE_POLICY`.
5. **Monetary Precision**: All monetary checks enforce Python `Decimal` arithmetic. Zero floats allowed.

## REST Endpoint
- `POST /api/v1/agents/{agent_id}/policies/evaluate`
