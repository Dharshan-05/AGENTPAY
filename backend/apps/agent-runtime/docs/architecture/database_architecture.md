# AGENTPAY Database Architecture & Strategy (Phase 011)

## Executive Summary

This document establishes the authoritative database architecture, domain ownership boundaries, data integrity rules, transaction strategy, security model, and environment standards for **AGENTPAY**.

The database architecture is designed to support high-throughput, financial-grade transactional safety for autonomous agent operations, AI-assisted commerce, user identity, and real-time security/fraud risk scoring.

---

## 1. Database Technology Selection

### Primary Transactional Database: PostgreSQL 15+

**PostgreSQL** is selected as the primary relational and transactional database for AGENTPAY based on the following core requirements:

1. **ACID Guarantees**: Strict Compliance with Atomicity, Consistency, Isolation, and Durability to prevent double-spending, inventory races, or inconsistent financial records.
2. **Relational Integrity**: Enforced at the engine layer via Foreign Keys, NOT NULL constraints, UNIQUE constraints, and CHECK constraints.
3. **Concurrency Control**: Multi-Version Concurrency Control (MVCC) and fine-grained row-level locking (`SELECT ... FOR UPDATE`) to handle high-concurrency payment execution and inventory locks.
4. **JSONB Semi-Structured Storage**: Hybrid relational + JSONB support for flexible metadata, AI explanation payloads (XAI/SHAP), provider-specific payment gateway responses, and dynamic agent configurations without schema pollution.
5. **Security & Governance**: Support for granular database roles, Row-Level Security (RLS) policies, encryption in transit (TLS/SSL), and auditing extensions.
6. **Scalability & Ecosystem**: Mature tooling for connection pooling (PgBouncer), read-replica scaling, point-in-time recovery (PITR), and zero-downtime schema migrations.

---

## 2. Logical Domain Architecture & Ownership Boundaries

To prevent uncontrolled cross-domain database writes and monolithic schema coupling, the AGENTPAY database is partitioned into four logical domain boundaries:

```text
                               ┌───────────────────────────┐
                               │     API / Gateway Layer   │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │ Application / Service     │
                               └─────────────┬─────────────┘
                                             │
      ┌────────────────────────┬─────────────┴───────────┬────────────────────────┐
      │                        │                         │                        │
┌─────▼──────────────┐  ┌──────▼──────────────┐   ┌──────▼──────────────┐  ┌──────▼──────────────┐
│  Identity Domain   │  │   Agent Domain      │   │   Commerce Domain   │  │ Security/Risk Domain│
├────────────────────┤  ├─────────────────────┤   ├─────────────────────┤  ├─────────────────────┤
│ • Users            │  │ • Agents            │   │ • Merchants         │  │ • Security Policies │
│ • User Profiles    │  │ • Agent Identity    │   │ • Products          │  │ • Policy Rules      │
│ • Roles            │  │ • Agent Credentials │   │ • Categories        │  │ • Policy Evaluation │
│ • Permissions      │  │ • Agent Sessions    │   │ • Inventory         │  │ • Behaviour Events  │
│ • User Roles       │  │ • Agent Roles       │   │ • Offers            │  │ • Risk Signals      │
│ • Sessions         │  │ • Agent Lifecycle   │   │ • Purchase Intent   │  │ • Fraud Predictions │
│ • Refresh Tokens   │  │ • Agent Trust       │   │ • Purchase Plans    │  │ • XAI Explanations  │
│ • Auth Events      │  │ • Agent Audit       │   │ • Transactions      │  │ • Audit Logs        │
└────────────────────┘  └─────────────────────┘   └─────────────────────┘  └─────────────────────┘
```

### Domain Data Ownership Rules

1. **Strict Service Ownership**: Each domain logic boundary owns its corresponding table schemas. Direct SQL cross-domain joins across domain boundaries from application services are prohibited.
2. **Repository Access Contract**: Services read or write data exclusively through designated Repository interfaces (`API -> Application Service -> Repository Layer -> PostgreSQL`).
3. **Cross-Domain Communication**: Inter-domain operations must occur via Application Service APIs or Domain Events, preserving microservice extraction readiness.

---

## 3. Transaction Strategy

### Isolation Levels & Transaction Boundaries

1. **Default Isolation Level**: `READ COMMITTED` for standard application reads and non-critical updates.
2. **Strict Financial & Inventory Isolation**: `SERIALIZABLE` or `REPEATABLE READ` with explicit pessimistic row locks (`SELECT ... FOR UPDATE`) for:
   - Wallet/Balance updates.
   - Commerce Transaction state execution (`PENDING` -> `SETTLED` / `FAILED`).
   - Inventory reservation locks.

### Transaction Invariants

- **Atomic Execution**: All multi-step financial or lifecycle state changes execute inside explicit database transactions.
- **Rollback Policy**: Any unhandled application error or validation failure triggers immediate database transaction rollback.
- **Idempotency Guarantee**: Financial transactions accept a mandatory client-provided or agent-generated `idempotency_key`. Re-submitted requests with identical keys yield cached execution results without re-executing state changes.
- **Deadlock Handling**: Data access repositories implement bounded exponential backoff retries (maximum 3 retries) for transient serialization failures (`40001` deadlock / serialization errors).

---

## 4. Data Integrity Strategy

Data integrity MUST be enforced at the database layer and NOT assumed solely from application-level validation:

1. **Primary Keys**: Every table defines an immutable `id` column using UUIDv7 format.
2. **Foreign Keys**: Enforced for all relational references with explicit delete actions (`ON DELETE RESTRICT` or `ON DELETE CASCADE` where cascading lifecycle ownership is explicit). Cascading deletes are strictly forbidden on financial transactions or security logs.
3. **NOT NULL Constraints**: Explicitly declared on all mandatory business columns.
4. **CHECK Constraints**: Applied for status enumerations, positive currency amounts (`amount >= 0`), non-negative inventory quantities (`quantity >= 0`), and valid numeric thresholds.
5. **UNIQUE Constraints**: Enforced for natural unique keys (e.g. `user_id + agent_name`, `email`, `idempotency_key`).

---

## 5. Primary Key & Identifier Strategy

### Canonical Format: UUIDv7 (Time-Ordered UUID)

AGENTPAY adopts **UUIDv7** for primary keys across all domain tables:

- **Global Uniqueness**: Eliminates ID collisions across distributed nodes and microservices.
- **Time-Ordered Indexing**: UUIDv7 embeds a 48-bit UTC millisecond timestamp prefix, ensuring sequential B-Tree index insertions and preventing database page fragmentation common with random UUIDv4.
- **Security**: Non-enumerable public identifiers prevent resource harvesting attacks (e.g. `/api/v1/orders/1` vs `/api/v1/orders/018f3a5b-7c1e-7234-8f92-123456789abc`).

---

## 6. Timestamp & Audit Field Strategy

All entities incorporate standardized timezone-aware UTC timestamps:

- `created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP`: Time of record creation.
- `updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP`: Time of last modification.
- `deleted_at TIMESTAMP WITH TIME ZONE NULL`: Timestamp for soft-deleted records.

---

## 7. Soft Delete & Immutability Strategy

### Record Classification

1. **Soft-Deletable Entities**: Users, Agents, Products, Merchants. Marked as deleted via `deleted_at IS NOT NULL`; filtered out by default queries.
2. **Immutable Append-Only Records**:
   - Financial Transactions
   - Audit Logs
   - Security Violations & Policy Evaluations
   - Fraud Risk Scores & XAI Explanations
   - Ledger Entries

Immutable records CANNOT be updated or deleted by standard application database roles.

---

## 8. Multi-Tenancy & Tenant Isolation Strategy

To support multi-merchant enterprise operations:

1. **Tenant-Scoped Schema Architecture**: All tenant-owned tables include a mandatory `tenant_id UUID NOT NULL` foreign key.
2. **Row-Level Security (RLS)**: Prepared for database-level RLS policies enforcing `tenant_id = current_setting('app.current_tenant_id')` during query execution.

---

## 9. Security & Secret Protection Strategy

1. **Principle of Least Privilege**:
   - **Application Role (`agentpay_app`)**: Granted `SELECT`, `INSERT`, `UPDATE`, `DELETE` on operational tables. Cannot alter schemas or drop tables.
   - **Migration Role (`agentpay_migrator`)**: Granted DDL execution (`CREATE`, `ALTER`, `DROP`) during automated CI/CD pipeline migrations.
   - **Analytics Role (`agentpay_analytics`)**: Granted read-only `SELECT` access to non-sensitive aggregated views.
2. **Encryption Standards**:
   - **In Transit**: Mandatory TLS 1.3 / SSL connection (`sslmode=verify-full` or `sslmode=require`).
   - **At Rest**: AES-256 transparent data encryption (TDE) at filesystem/volume layer.
   - **Column-Level Encryption**: Sensitive credentials (agent tokens, API keys) encrypted via AES-GCM before storage.
3. **Zero Plaintext Secrets**: Passwords hashed via Argon2id or Bcrypt. Secrets wrapped in `SecretStr` in application code.

---

## 10. Audit Log Schema Strategy

Immutable audit trails capture operational and security events using a canonical structure:

```json
{
  "id": "018f3a5b-7c1e-7234-8f92-123456789abc",
  "actor_id": "018f3a5b-0000-7000-8000-000000000001",
  "actor_type": "user",
  "action": "agent.credential.rotate",
  "resource": "agent_credential",
  "resource_id": "018f3a5b-0000-7000-8000-000000000099",
  "timestamp": "2026-08-25T19:00:00.000Z",
  "result": "SUCCESS",
  "request_id": "req_87654321",
  "correlation_id": "corr_12345678",
  "metadata": {
    "ip_address": "127.0.0.1",
    "user_agent": "AgentPay-Runtime/1.0"
  }
}
```

---

## 11. Environment Separation & Data Handling

| Environment | Purpose | Database Instance | Credentials Source |
| :--- | :--- | :--- | :--- |
| **Development** | Local coding & debugging | Local Docker Container (`agentpay-postgres`) | `.env` / `.env.example` |
| **Test** | CI/CD Automated Pytest | Isolated Test Container (`agentpay_test`) | Pytest environment fixtures |
| **Staging** | Pre-production validation | Managed PostgreSQL Cloud Instance | Secret Manager |
| **Production** | Live enterprise service | Managed High-Availability PostgreSQL Cluster | IAM / Secret Manager |

*Production data is strictly forbidden from being copied into local development or test environments.*
