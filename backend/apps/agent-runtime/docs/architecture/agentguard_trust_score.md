# AGENTGUARD Architecture Specification: Phase 206 — Agent Trust Score

## Overview
Phase 206 implements `AgentTrustScoreService`, providing a structured Decimal representation of an agent's trust score.

## Score Model & States
- **Score Representation**: Bounded Decimal from `0.00` to `1.00`.
- **States**: `TRUSTED` (>=0.85), `NORMAL` (>=0.65), `CAUTION` (>=0.45), `HIGH_RISK` (>=0.25), `UNTRUSTED` (<0.25), `COLD_START`.
- **Tenant Isolation**: Strictly scoped by `tenant_id` AND `agent_id`.
- **Integration**: Advisory subsystem used in trust score calculations.
