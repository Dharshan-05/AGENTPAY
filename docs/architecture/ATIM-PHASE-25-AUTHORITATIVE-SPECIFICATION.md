# ATIM PHASE 25 — AUTHORITATIVE SPECIFICATION

**System**: AGENTPAY ATIM (Autonomous Transaction Intelligence & Management)  
**Group**: 14  
**Phase**: 025  
**Title**: ATIM Autonomous Market Clearing & Multi-Agent Settlement Engine  
**Status**: SPECIFICATION DESIGNED — IMPLEMENTATION NOT AUTHORIZED  
**Target Migration**: 049 (PROPOSED DESIGN DECISION — NOT CREATED)  
**Target ORM Tables**: 75 (PROPOSED DESIGN DECISION — NOT CREATED)  

---

## 1. DOCUMENT CONTROL

- **PHASE**: 25
- **GROUP**: 14
- **TITLE**: ATIM Autonomous Market Clearing & Multi-Agent Settlement Engine
- **STATUS**: SPECIFICATION DESIGNED
- **IMPLEMENTATION STATUS**: NOT IMPLEMENTED / NOT AUTHORIZED
- **AUTHORITY**: ATIM ARCHITECTURE
- **VERSION**: 1.0
- **DATE**: 2026-08-31
- **DEPENDENCIES**: Group 11 (Phases 21 & 22 Idempotency & Recovery), Group 12 (Phase 23 Durable Workflows), Group 13 (Phase 24 Multi-Agent Distributed Consensus).

---

## 2. PURPOSE

ATIM Phase 25 defines the authoritative specification for the **Autonomous Market Clearing & Multi-Agent Settlement Engine**. Following Phase 23 (Durable Workflows) and Phase 24 (Multi-Agent Distributed Consensus), Phase 25 addresses the critical architectural gap of deterministic transaction clearing and balance settlement across autonomous agent accounts and merchant ledgers.

When multi-agent consensus is reached under Phase 24, the underlying financial obligations must be cleared, held in escrow (where required), and settled with zero double-execution, explicit transactional locks, and strict financial precision (`Decimal` / PostgreSQL `NUMERIC(18,4)`). Phase 25 guarantees that multi-party consensus decisions translate into atomic, immutable ledger postings without giving LLMs financial execution authority.

---

## 3. SCOPE

### IN SCOPE (PROPOSED DESIGN DECISION)
- **Settlement & Clearing Domain**: Concepts for market clearing batches, settlement instructions, and escrow holds.
- **Atomic Clearing Protocol**: Double-entry ledger settlement model between buyer agents, merchant accounts, and platform fees.
- **Settlement Lifecycle State Machine**: States (`PENDING`, `HELD_IN_ESCROW`, `SETTLING`, `SETTLED`, `DISPUTED`, `REFUNDED`, `FAILED`).
- **Database Schema Design**: Tables `atim_settlement_batches` and `atim_settlement_entries` (Conceptual design only; no migration created).
- **REST API Specifications**: Proposed endpoints for querying settlement status and batch instructions.
- **Integrations**: Formal contracts with AgentGuard, FraudGuard, HITL, Phase 23 Workflows, and Phase 24 Consensus.

### OUT OF SCOPE
- **DO NOT** execute production database migrations (Migration 049 is NOT created).
- **DO NOT** create ORM Python model files or service code.
- **DO NOT** replace or modify existing PostgreSQL, Redis, Supabase, or Gemini integrations.
- **DO NOT** implement Phase 26 or future roadmap items.

---

## 4. ARCHITECTURAL POSITION

Phase 25 occupies the settlement and clearing layer following multi-agent consensus and prior to external payment gateway dispatch:

```
WEB / HTTP CLIENT
        ↓
FASTAPI ROUTE
        ↓
AUTHENTICATION & TENANT RESOLUTION
        ↓
AGENT IDENTITY VERIFICATION
        ↓
ATIM CORE AUTHORIZATION SERVICE
        ↓
AGENTGUARD & FRAUDGUARD ADVISORY CHECKS
        ↓
LLM PROPOSAL ENGINE (Gemini Provider)
        ↓
PHASE 23 DURABLE WORKFLOW ORCHESTRATION
        ↓
PHASE 24 MULTI-AGENT CONSENSUS VERIFICATION
        ↓
PHASE 25 AUTONOMOUS MARKET CLEARING & SETTLEMENT ENGINE
        ├── Escrow & Hold Verification
        ├── Double-Entry Ledger Posting
        └── Atomic Settlement Execution
        ↓
EXTERNAL PAYMENT GATEWAY (Optional Dispatch)
        ↓
HMAC-SHA256 AUDIT LOGGING & OUTBOX EVENT GENERATION
```

---

## 5. DOMAIN MODEL SPECIFICATION (PROPOSED DESIGN DECISION)

- `SettlementStatus`: Enum (`PENDING`, `HELD_IN_ESCROW`, `SETTLING`, `SETTLED`, `DISPUTED`, `REFUNDED`, `FAILED`).
- `SettlementType`: Enum (`IMMEDIATE`, `ESCROW_RELEASE`, `NET_BATCH_SETTLEMENT`).
- `SettlementBatchRecord`: Domain model representing a aggregated clearing batch.
- `SettlementEntryRecord`: Domain model representing an individual credit/debit ledger posting.

*Invariants*:
- All monetary values must use `Decimal` with 4 decimal places of precision (`NUMERIC(18,4)`).
- Total debits must equal total credits in every settlement batch (`sum(debits) == sum(credits)`).

---

## 6. DATABASE DESIGN (CONCEPTUAL DESIGN ONLY — NO MIGRATION CREATED)

### Table 1: `atim_settlement_batches` (PROPOSED)
- `id`: `UUID` (Primary Key, default `uuid.uuid4`)
- `tenant_id`: `UUID` (Indexed, Foreign Key to `tenants.id`)
- `consensus_session_id`: `UUID` (Nullable, Foreign Key to `atim_consensus_sessions.id`)
- `workflow_id`: `UUID` (Nullable, Foreign Key to `atim_workflow_instances.id`)
- `settlement_type`: `VARCHAR(32)` (Not Null)
- `total_amount`: `NUMERIC(18,4)` (Not Null, Non-negative)
- `currency`: `VARCHAR(3)` (Not Null, Default `'USD'`)
- `status`: `VARCHAR(32)` (Not Null, Default `'PENDING'`)
- `created_at`: `TIMESTAMPTZ` (Not Null)
- `settled_at`: `TIMESTAMPTZ` (Nullable)

### Table 2: `atim_settlement_entries` (PROPOSED)
- `id`: `UUID` (Primary Key, default `uuid.uuid4`)
- `batch_id`: `UUID` (Indexed, Foreign Key to `atim_settlement_batches.id`)
- `tenant_id`: `UUID` (Indexed)
- `account_id`: `UUID` (Indexed)
- `entry_type`: `VARCHAR(16)` (Not Null: `'DEBIT'` or `'CREDIT'`)
- `amount`: `NUMERIC(18,4)` (Not Null)
- `description`: `VARCHAR(256)` (Nullable)
- `created_at`: `TIMESTAMPTZ` (Not Null)

*Note*: **NO MIGRATION HAS BEEN CREATED. DATABASE REMAINS UNCHANGED (73 ORM TABLES).**

---

## 7. STATE MACHINES

```
[PENDING] ──┬──> [HELD_IN_ESCROW] ──> [SETTLING] ──> [SETTLED] (Terminal Success)
            │                           │
            ├──> [SETTLING] ────────────┴──> [FAILED] (Terminal Failure)
            │
            └──> [CANCELLED] (Terminal Abort)
```

---

## 8. SERVICE ARCHITECTURE (PROPOSED DESIGN DECISION)

- `ATIMSettlementService`: Responsible for ledger entry validation, escrow lock verification, and atomic batch settlement.
- `ATIMEscrowEngine`: Manages conditional holding and release of funds tied to Phase 23 workflow triggers.

---

## 9. API CONTRACTS (PROPOSED DESIGN DECISION)

### `POST /api/v1/atim/settlements/batches`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "tenant_id": "uuid",
    "consensus_session_id": "uuid",
    "workflow_id": "uuid",
    "settlement_type": "IMMEDIATE",
    "amount": "150.0000",
    "currency": "USD"
  }
  ```
- **Response**: `201 Created` with settlement batch details.

---

## 10. SECURITY MODEL

- **Server-Authoritative Tenant Boundary**: All queries and mutations enforce `tenant_id == current_user.tenant_id`.
- **Double-Execution Prevention**: Mandatory idempotency key check over `(tenant_id, consensus_session_id, operation)`.
- **RBAC**: Requires `agent:settlement:execute` permission.

---

## 11. LLM SECURITY BOUNDARY

- **LLM MAY**: Analyze settlement risk factors, suggest batch groupings, summarize transaction histories.
- **LLM MUST NOT**: Authorize settlement execution, alter ledger amounts, bypass escrow requirements, or grant financial clearance.
- **LLM Zero Authority**: The LLM remains an untrusted proposal engine with **ZERO FINANCIAL AUTHORITY**.

---

## 12. AGENTGUARD INTEGRATION

AgentGuard evaluates agent execution limits prior to settlement batch creation. If AgentGuard denies the transaction, settlement transitions immediately to `FAILED` with `AGENTGUARD_DENIED` status.

---

## 13. FRAUDGUARD INTEGRATION

FraudGuard evaluates risk scores for account entries. Settlements exceeding risk thresholds require HITL approval before transitioning from `HELD_IN_ESCROW` to `SETTLING`.

---

## 14. HITL INTEGRATION

High-value settlements (> $10,000.0000) trigger human-in-the-loop review. The settlement remains in `HELD_IN_ESCROW` state until a signed human approval decision is submitted.

---

## 15. WORKFLOW INTEGRATION

Phase 25 settlement steps integrate as step executions within Phase 23 durable workflow instances. Failure of a settlement step triggers workflow rollback or compensation steps.

---

## 16. CONSENSUS INTEGRATION

Settlement batch execution requires a valid Phase 24 consensus session with `status == QUORUM_REACHED`. Sessions in `VOTING`, `QUORUM_FAILED`, or `EXPIRED` states cannot trigger settlement.

---

## 17. FINANCIAL SAFETY

- **No Float Types**: `float` and `double` types are strictly forbidden. All monetary amounts use `Decimal` / PostgreSQL `NUMERIC(18,4)`.
- **Transactional Atomicity**: All entries within a settlement batch are posted inside a single PostgreSQL transaction (`BEGIN...COMMIT`).

---

## 18. AUDIT MODEL

Every settlement state transition produces an immutable audit record signed using HMAC-SHA256 over `(batch_id, tenant_id, amount, status, timestamp)`.

---

## 19. OBSERVABILITY

- Metrics: `atim_settlement_batches_total`, `atim_settlement_amount_total`, `atim_settlement_latency_seconds`.
- Tracing: OpenTelemetry spans covering ledger posting and escrow locks.

---

## 20. ERROR MODEL

- `SettlementError`: Base exception for clearing failures.
- `LedgerImbalanceError`: Raised when debits do not equal credits.
- `EscrowLockError`: Raised when escrow release conditions fail.

---

## 21. FAILURE & RECOVERY

If PostgreSQL or network connections drop during settlement execution, the operation rolls back atomically. Retries use existing Group 11 idempotency locks to prevent double clearing.

---

## 22. DATA RETENTION

Settlement batches and ledger entries must be retained for 7 years to meet financial compliance requirements.

---

## 23. PERFORMANCE REQUIREMENTS

- Batch Clearing Processing Latency: < 50ms (p95).
- Throughput Target: > 500 settlement entries/sec under transaction locks.

---

## 24. COMPLIANCE REQUIREMENTS

Supports double-entry bookkeeping standards and SOC2/PCI-DSS audit trail verification.

---

## 25. TESTING REQUIREMENTS (PROPOSED FOR FUTURE IMPLEMENTATION)

- Unit tests: `test_atim_settlement_service.py` (Ledger balance checks, escrow state transitions).
- Integration tests: `test_atim_settlement_api.py` (REST endpoint E2E testing).
- Security tests: `test_atim_group14_security.py` (Double-clearing prevention, cross-tenant isolation).

---

## 26. MIGRATION PLAN

- **Migration Revision**: `049_atim_autonomous_market_clearing.py` (PROPOSED DESIGN DECISION — NOT CREATED).
- **Current Alembic Head**: `048_atim_multi_agent_consensus.py` (UNCHANGED).

---

## 27. IMPLEMENTATION BOUNDARY

The future implementation MAY add domain models, ORM models, migration 049, services, and tests for Phase 25. It MUST NOT modify existing Phase 1-24 code or weaken security controls.

---

## 28. DEPENDENCY MAP

```
Phase 21/22 (Idempotency & Outbox)
        ↓
Phase 23 (Durable Workflows)
        ↓
Phase 24 (Multi-Agent Consensus)
        ↓
Phase 25 (Autonomous Market Clearing & Settlement Engine)
```

---

## 29. SECURITY INVARIANTS

- **INV-001**: LLM SHALL HAVE ZERO FINANCIAL AUTHORITY.
- **INV-002**: NO CROSS-TENANT DATA ACCESS.
- **INV-003**: NO DOUBLE FINANCIAL EXECUTION.
- **INV-004**: TOTAL DEBITS SHALL EQUAL TOTAL CREDITS IN EVERY SETTLEMENT BATCH.
- **INV-005**: SETTLEMENT SHALL REQUIRE QUORUM_REACHED CONSENSUS STATUS FOR HIGH-RISK ACTIONS.

---

## 30. ACCEPTANCE CRITERIA (FOR FUTURE IMPLEMENTATION)

1. Double-entry ledger balance assertion (`debits == credits`) enforced on all batches.
2. Full test suite baseline of 229 tests remains passing.
3. Cross-tenant settlement requests rejected with `403 Forbidden`.
4. Zero `float` usage across all monetary models and columns.

---

## 31. REGRESSION PROTECTION

Preservation of current test suite baseline (**229 PASSED, 0 FAILED**) is mandatory.

---

## 32. FUTURE IMPLEMENTATION GATE

```text
PHASE 25 IMPLEMENTATION:
NOT AUTHORIZED BY THIS DOCUMENT

This specification grants design authority only.
Implementation requires separate explicit user authorization.
```
