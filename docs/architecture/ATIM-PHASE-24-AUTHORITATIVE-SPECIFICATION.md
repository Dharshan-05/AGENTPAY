# ATIM PHASE 24 — AUTHORITATIVE SPECIFICATION

**System**: AGENTPAY ATIM (Autonomous Transaction Intelligence & Management)  
**Group**: 13  
**Phase**: 024  
**Title**: ATIM Multi-Agent Distributed Consensus & Transactional Multi-Party Governance  
**Status**: SPECIFICATION DEFINED — IMPLEMENTATION NOT STARTED  
**Target Migration**: 048  
**ORM Tables Target**: 73  

---

## 1. Executive Summary

ATIM Phase 24 defines the authoritative specification for **Multi-Agent Distributed Consensus & Transactional Multi-Party Governance**. Building directly upon Phase 23 (Durable Execution Orchestration & Workflow State Management), Phase 24 extends single-agent workflow execution into a multi-agent distributed consensus framework. When complex autonomous commerce operations require multi-agent agreement (e.g., Buyer Agent, Treasury Agent, Compliance Verification Agent, Risk Assessment Agent), Phase 24 provides a deterministic cryptographic consensus protocol, quorum verification, and threshold signature approval before financial execution is permitted.

---

## 2. Current Baseline

- **Group 11 (Phases 21 & 22)**: ATIM Distributed State, Idempotency, Transaction Consistency, Advanced Reliability, Recovery, and Durable Outbox — **COMPLETE & VERIFIED**.
- **Group 12 (Phase 23)**: ATIM Durable Execution Orchestration & Workflow State Management — **COMPLETE & VERIFIED** (Migration `047`, 71 ORM Tables).
- **LLM Provider Architecture**: `GeminiProvider` implemented behind `ILLMProvider` interface, live verified against Google Gemini API (`gemini-3.6-flash`).
- **Real Web/API LLM Pipeline**: `POST /api/v1/atim/analyze` live verified.
- **Full Test Baseline**: **222 PASSED, 0 FAILED**.
- **Core Security Invariant**: LLM is an untrusted proposal engine with **ZERO FINANCIAL AUTHORITY**.

---

## 3. Phase 24 Purpose

The purpose of Phase 24 is to establish a deterministic multi-agent governance boundary. In complex enterprise agentic commerce, single-agent proposals are vulnerable to single-point-of-compromise. Phase 24 enforces multi-agent quorum verification where multiple distinct autonomous agents must independently evaluate, sign, and vote on high-risk transaction proposals before AgentGuard, FraudGuard, and HITL authorization can take effect.

---

## 4. Problem Statement

Prior to Phase 24, workflows orchestrated multiple steps sequentially, but all steps were proposed or driven by a single primary agent identity. In high-value corporate purchasing, treasury management, or supply chain payments:
1. A single compromised agent identity could propose unauthorized high-value commitments.
2. Single-agent approval lacks separation-of-duties (SoD) enforcement across autonomous roles.
3. Complex multi-party transactions require atomic agreement across independent agent identities under strict cryptographic proof.

Phase 24 resolves this by introducing **Multi-Agent Quorum Consensus**, **Role-Based Agent Separation of Duties**, and **Cryptographic Quorum Evidence Logging**.

---

## 5. Scope

- **Multi-Agent Consensus Protocol**: Domain models, quorum rules, voting mechanisms (`APPROVE`, `REJECT`, `ABSTAIN`).
- **Separation of Duties (SoD) Engine**: Enforcement that proposing, verifying, and approving agents must have distinct `agent_id`s and orthogonal role authorizations.
- **Quorum State Machine**: States (`INITIATED`, `VOTING`, `QUORUM_REACHED`, `QUORUM_FAILED`, `EXPIRED`, `CANCELLED`).
- **DB Persistence**: Tables `atim_consensus_sessions` and `atim_consensus_votes`.
- **REST APIs**: `POST /api/v1/atim/consensus/sessions` and `GET /api/v1/atim/consensus/sessions/{session_id}`.
- **HMAC Audit Logging**: Immutable tamper-evident consensus audit entries signed with server secret.

---

## 6. Non-Scope

- **DO NOT** modify existing Phase 23 workflow tables or Phase 21 outbox schemas.
- **DO NOT** give LLM models consensus authority or voting rights.
- **DO NOT** execute real blockchain smart contracts or external decentralized ledgers.
- **DO NOT** implement Phase 25 (Autonomous Market Clearing) or any future phase.

---

## 7. Architecture

```
HTTP/WEB API
    ↓
FastAPI Route (/api/v1/atim/consensus)
    ↓
Authentication & Tenant Resolution
    ↓
ATIM Multi-Agent Consensus Orchestrator
    ├── Agent Identity & SoD Validation
    ├── Quorum Threshold & Policy Verification
    ├── Agent Vote Cryptographic Verification
    └── Consensus State Machine Evaluation
    ↓
AgentGuard & FraudGuard Advisory Check
    ↓
HMAC-SHA256 Audit Trail & Outbox Event Generation
    ↓
Deterministic Execution / Failure Decision
```

---

## 8. Domain Model

- `ConsensusSessionStatus`: Enum (`INITIATED`, `VOTING`, `QUORUM_REACHED`, `QUORUM_FAILED`, `EXPIRED`, `CANCELLED`).
- `VoteType`: Enum (`APPROVE`, `REJECT`, `ABSTAIN`).
- `ConsensusSessionRecord`: Domain model representing a multi-agent consensus session.
- `ConsensusVoteRecord`: Domain model representing an individual agent's vote.

---

## 9. Database Model

### Table 1: `atim_consensus_sessions`
- `id`: `UUID` (Primary Key)
- `tenant_id`: `UUID` (Indexed, Foreign Key to `tenants.id`)
- `proposer_agent_id`: `UUID` (Indexed, Foreign Key to `agents.id`)
- `workflow_id`: `UUID` (Nullable, Foreign Key to `atim_workflow_instances.id`)
- `action`: `VARCHAR(64)` (Not Null)
- `required_quorum`: `INTEGER` (Not Null, Min 2)
- `status`: `VARCHAR(32)` (Not Null, Default `'INITIATED'`)
- `created_at`: `TIMESTAMPTZ` (Not Null)
- `expires_at`: `TIMESTAMPTZ` (Not Null)

### Table 2: `atim_consensus_votes`
- `id`: `UUID` (Primary Key)
- `session_id`: `UUID` (Indexed, Foreign Key to `atim_consensus_sessions.id`)
- `tenant_id`: `UUID` (Indexed)
- `voter_agent_id`: `UUID` (Indexed, Foreign Key to `agents.id`)
- `vote`: `VARCHAR(16)` (Not Null)
- `reason`: `VARCHAR(512)` (Nullable)
- `vote_signature`: `VARCHAR(256)` (Not Null, HMAC-SHA256)
- `voted_at`: `TIMESTAMPTZ` (Not Null)

*Constraints*: Unique constraint `uq_session_voter (session_id, voter_agent_id)`.

---

## 10. Service Architecture

- `ATIMConsensusService`: Manages session creation, vote recording, SoD validation, and quorum evaluation.
- `ATIMConsensusStateEngine`: Enforces deterministic state transitions for consensus sessions.

---

## 11. API Contracts

### `POST /api/v1/atim/consensus/sessions`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "tenant_id": "uuid",
    "proposer_agent_id": "uuid",
    "workflow_id": "uuid",
    "action": "PURCHASE_APPROVAL",
    "required_quorum": 3,
    "timeout_seconds": 300
  }
  ```
- **Response**: `201 Created` with `ConsensusSessionResponse`.

### `POST /api/v1/atim/consensus/sessions/{session_id}/vote`
- **Request Body**:
  ```json
  {
    "voter_agent_id": "uuid",
    "vote": "APPROVE",
    "reason": "Risk score within acceptable thresholds"
  }
  ```
- **Response**: `200 OK` with updated session status.

---

## 12. LLM Integration

- LLM models (e.g., Gemini) provide **intent analysis and risk signals only**.
- LLMs **CANNOT** cast votes, create consensus sessions, or override quorum requirements.
- LLM outputs passed into consensus sessions are validated as untrusted strings.

---

## 13. Security Architecture

- **Separation of Duties (SoD)**: Proposer agent cannot vote in its own session (`voter_agent_id != proposer_agent_id`).
- **Server Authoritative Tenant Boundary**: `tenant_id` must match `current_user.tenant_id`.
- **HMAC Audit Signing**: Every vote is signed using server HMAC secret over `(session_id, voter_agent_id, vote, voted_at)`.

---

## 14. Tenant Isolation

All consensus sessions and votes are filtered by `tenant_id`. Cross-tenant voting or session querying is strictly rejected with `HTTP 403 Forbidden`.

---

## 15. Agent Isolation

Agent credentials and role signatures are validated. An agent cannot vote on behalf of another `agent_id`.

---

## 16. RBAC

Voting agents must possess the `agent:consensus:vote` permission. Proposing agents must possess the `agent:consensus:propose` permission.

---

## 17. Failure Model

- **Quorum Timeout**: Session transitions to `EXPIRED` if quorum is not reached before `expires_at`.
- **Rejection Quorum**: Session transitions to `QUORUM_FAILED` immediately if rejections make reaching quorum impossible.
- **Fail-Closed**: Unhandled exceptions result in `DENY` decision.

---

## 18. State Machines

```
[INITIATED] ──> [VOTING] ──┬──> [QUORUM_REACHED] (Terminal Success)
                          ├──> [QUORUM_FAILED]  (Terminal Failure)
                          ├──> [EXPIRED]        (Terminal Timeout)
                          └──> [CANCELLED]      (Terminal Abort)
```

---

## 19. Audit Requirements

All session creations, votes, and state transitions generate structured HMAC-signed audit logs with correlation IDs.

---

## 20. Observability

- Metrics: `atim_consensus_sessions_total`, `atim_consensus_votes_total`, `atim_consensus_latency_seconds`.
- Tracing: OpenTelemetry spans for consensus evaluation.

---

## 21. Test Strategy

- **Unit Tests**: `test_atim_consensus_service.py` (Session creation, voting logic, SoD enforcement).
- **Integration Tests**: `test_atim_consensus_api.py` (REST endpoint E2E testing).
- **Security Tests**: `test_atim_group13_security.py` (Cross-tenant voting rejection, self-voting prevention, prompt injection resilience).

---

## 22. Regression Contract

The existing baseline of **222 PASSED, 0 FAILED** tests must be preserved without modification or deletion.

---

## 23. Implementation Order

1. Domain models (`app/domain/governance/consensus_models.py`).
2. ORM models (`app/infrastructure/database/models/atim_consensus.py`).
3. Alembic migration `048_atim_multi_agent_consensus.py`.
4. Consensus application service (`app/application/services/atim_consensus_service.py`).
5. REST API routes (`app/api/v1/atim.py`).
6. Unit, integration, and security test suites.

---

## 24. Acceptance Criteria

- Quorum verification logic correctly calculates required votes.
- SoD engine strictly blocks proposer self-voting.
- HMAC signatures prevent vote tampering.
- API endpoints return correct HTTP status codes under all scenarios.
- 222 existing tests continue to pass cleanly.

---

## 25. Security Invariants

1. **LLM ZERO AUTHORITY**: LLM cannot vote or authorize transactions.
2. **STRICT SoD**: `proposer_agent_id != voter_agent_id`.
3. **TENANT ISOLATION**: Cross-tenant operations strictly forbidden.
4. **FAIL-CLOSED**: System defaults to `DENY` / `QUORUM_FAILED` on errors.

---

## 26. Explicit Prohibitions

- **DO NOT** use float data types for monetary or voting thresholds.
- **DO NOT** expose API keys or secrets in logs or responses.
- **DO NOT** bypass AgentGuard, FraudGuard, or HITL controls.

---

## 27. Future Phase Boundary

- **Phase 25+**: Autonomous Market Clearing, Cross-Chain Liquidity Protocols, or Decentralized Clearing Nodes belong strictly to future phases.

---

## 28. Final Authority Statement

This document constitutes the sole authoritative architectural specification for **ATIM Phase 24 (Group 13)**. No implementation work shall proceed without explicit user authorization.
