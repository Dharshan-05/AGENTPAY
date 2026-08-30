# AGENTPAY — User Management Functional Specifications

## 1. Overview

User Management functions specify user profile administration, notification settings, security credentials, and multi-agent ownership controls.

---

## 2. Specifications

### FR-USER-001: User Account Profile & Security Settings
* **FR ID**: `FR-USER-001`
* **Title**: User Account Profile Management & Security Controls
* **Source**: `REQ-USR-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: View and update account profile, password, and security preferences.
* **Preconditions**: User is authenticated with an active session.
* **Trigger**: User navigates to Account Settings page and submits updates.
* **Inputs**: `full_name` (optional), `current_password` (string), `new_password` (optional).
* **Main Flow**:
  1. User submits profile update request.
  2. System verifies active user JWT session.
  3. If password change requested, system verifies `current_password` hash.
  4. System hashes `new_password` using Argon2id and updates database.
  5. System invalidates existing refresh tokens and issues confirmation email.
* **Alternative Flows**:
  * *AF-1 (Wrong Password)*: Return `ERR_INVALID_PASSWORD`.
* **Business Rules**: `BR-001`.
* **Validation Rules**: `new_password` length $\ge 12$ chars.
* **Authorization Rules**: Requires active session matching target `user_id`.
* **State Changes**: User profile record updated.
* **Outputs**: Success confirmation JSON.
* **Error Conditions**: `ERR_INVALID_PASSWORD`, `ERR_UNAUTHORIZED`.
* **Security Requirements**: Password update invalidates active sessions except current.
* **Audit Events**: `EVENT_USER_PROFILE_UPDATED`, `EVENT_PASSWORD_CHANGED`.
* **Acceptance Criteria**: `AC-USR-001`.
* **Dependencies**: `FR-AUTH-002`.

---

### FR-USER-002: User Multi-Agent Ownership & Inventory View
* **FR ID**: `FR-USER-002`
* **Title**: Multi-Agent Ownership Inventory Console
* **Source**: `REQ-USR-006`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: View comprehensive list of all owned AI AGENT entities and real-time statuses.
* **Preconditions**: User is authenticated.
* **Trigger**: User opens Agent Management section on Web Dashboard.
* **Inputs**: Query parameters (`status_filter`, `page`, `limit`).
* **Main Flow**:
  1. System queries database for agents where `owner_id == authenticated_user_id`.
  2. System attaches real-time Redis state (`ACTIVE`, `PAUSED`, `SUSPENDED`, `REVOKED`).
  3. System attaches 24-hour spending summary metrics for each agent.
  4. System renders agent inventory table.
* **Business Rules**: `BR-001`, `BR-007`.
* **Authorization Rules**: Users can ONLY view agents they explicitly own.
* **Outputs**: Array of Agent JSON objects with real-time state flags.
* **Audit Events**: None (read query).
* **Acceptance Criteria**: `AC-USR-002`.
* **Dependencies**: `FR-AGENT-001`.
