# AGENTPAY — Agent Registration & Lifecycle Functional Specifications

## 1. Overview

Agent Registration & Lifecycle functions govern agent onboarding, HMAC key generation, state transitions, and hard credential revocation.

---

## 2. Specifications

### FR-AGENT-001: Agent Enrolment & Owner Assignment
* **FR ID**: `FR-AGENT-001`
* **Title**: AI Agent Enrolment & Ownership Binding
* **Source**: `REQ-AGENT-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: Register a new AI AGENT entity bound to the user's account.
* **Preconditions**: User is authenticated with active session.
* **Trigger**: User clicks "Register New AI Agent" and submits registration metadata.
* **Inputs**: `agent_name` (string), `purpose_description` (string), `initial_scope` (array).
* **Main Flow**:
  1. User enters agent name (e.g. "Procurement Bot Alpha") and purpose description.
  2. System generates unique `Agent ID` (UUID v4 format: `agt_8f9b2c3a-4e1d-4a5b`).
  3. System binds `owner_id = authenticated_user_id`.
  4. System initializes agent state to `REGISTERED`.
  5. System triggers HMAC Secret Key Generation (`FR-AGENT-002`).
* **Business Rules**: `BR-001`, `BR-007`.
* **Validation Rules**: `agent_name` length 3 - 50 chars; non-empty.
* **Authorization Rules**: Authenticated users only.
* **State Changes**: Agent record created in DB in `REGISTERED` state.
* **Outputs**: Agent metadata object and plaintext secret key (displayed ONCE).
* **Error Conditions**: `ERR_INVALID_AGENT_NAME`, `ERR_MAX_AGENTS_REACHED`.
* **Security Requirements**: Plaintext secret key displayed once in UI modal; never retrievable again.
* **Audit Events**: `EVENT_AGENT_REGISTERED`.
* **Acceptance Criteria**: `AC-AGENT-001`.
* **Dependencies**: `FR-AUTH-002`.

---

### FR-AGENT-002: Cryptographic HMAC Secret Key Generation
* **FR ID**: `FR-AGENT-002`
* **Title**: Cryptographic HMAC Key Issuance & Single Display Protocol
* **Source**: `REQ-AGENT-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: System (`SYSTEM`)
* **Goal**: Generate a 256-bit secret key for agent HMAC authentication.
* **Preconditions**: Agent record initialized via `FR-AGENT-001`.
* **Trigger**: System agent enrolment handler execution.
* **Inputs**: `agent_id` (string).
* **Main Flow**:
  1. System generates 256 bits (32 bytes) of cryptographically secure random data using CSPRNG (`crypto.randomBytes(32)`).
  2. System formats raw key as hex string (`sk_live_...`).
  3. System computes Argon2id hash of secret key.
  4. System stores Argon2id key hash in database record.
  5. System transmits plaintext secret key to frontend response payload ONCE.
* **Business Rules**: `BR-001`, `BR-007`.
* **State Changes**: Key hash stored in DB; Redis edge authentication index initialized.
* **Outputs**: `secret_key` string (transmitted once).
* **Security Requirements**: Plaintext key NEVER written to database or application logs.
* **Audit Events**: `EVENT_AGENT_KEY_ISSUED`.
* **Acceptance Criteria**: `AC-AGENT-001`.
* **Dependencies**: `FR-AGENT-001`.

---

### FR-AGENT-003: Agent Lifecycle State Machine Transitions
* **FR ID**: `FR-AGENT-003`
* **Title**: Agent Lifecycle State Transitions (`ACTIVE`, `PAUSED`, `SUSPENDED`, `REVOKED`)
* **Source**: `REQ-AGENT-003`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`) / System (`SYSTEM`)
* **Goal**: Transition agent between lifecycle states according to state machine rules.
* **Preconditions**: Agent exists and is owned by authenticated user.
* **Trigger**: User clicks pause/resume/revoke button OR system security alert triggers suspension.
* **Inputs**: `agent_id` (string), `target_state` (`ACTIVE`, `PAUSED`, `SUSPENDED`, `REVOKED`), `reason` (string).
* **Main Flow**:
  1. System checks current state and verifies legal transition matrix:
     * `REGISTERED` $\rightarrow$ `ACTIVE`
     * `ACTIVE` $\leftrightarrow$ `PAUSED`
     * `ACTIVE` / `PAUSED` $\rightarrow$ `SUSPENDED`
     * `ANY` $\rightarrow$ `REVOKED`
  2. System updates database state record atomically.
  3. System updates Redis edge state index (`agent:state:<agent_id>`).
  4. If target state is `SUSPENDED` or `REVOKED`, system purges edge authentication keys in $< 10\text{ ms}$.
* **Alternative Flows**:
  * *AF-1 (Illegal Transition)*: If transition is illegal (e.g. `REVOKED` $\rightarrow$ `ACTIVE`), reject with `ERR_ILLEGAL_STATE_TRANSITION`.
* **Business Rules**: `BR-007`.
* **State Changes**: Agent lifecycle state updated in DB and Redis cache.
* **Outputs**: Updated agent status JSON object.
* **Error Conditions**: `ERR_ILLEGAL_STATE_TRANSITION`, `ERR_AGENT_NOT_FOUND`.
* **Audit Events**: `EVENT_AGENT_STATE_TRANSITION`.
* **Acceptance Criteria**: `AC-AGENT-003`.
* **Dependencies**: `FR-AGENT-001`.
