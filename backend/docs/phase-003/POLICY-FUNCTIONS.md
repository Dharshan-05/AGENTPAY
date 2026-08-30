# AGENTPAY — User Policy Functional Specifications

## 1. Overview

User Policy functions specify rule definitions, policy configuration UIs, rule persistence, edge caching, and rule enforcement mechanisms across spending limits, category rules, and temporal boundaries.

---

## 2. Specifications

### FR-POLICY-001: Single Transaction Limit Rule Setup & Enforcement
* **FR ID**: `FR-POLICY-001`
* **Title**: Single Transaction Limit Configuration & Boundary Rule Check
* **Source**: `REQ-POLICY-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`) / AGENTGUARD
* **Goal**: Define and enforce a maximum currency ceiling for individual intent requests.
* **Preconditions**: User is authenticated; target agent is active.
* **Trigger**: User sets limit in UI OR AGENTGUARD evaluates incoming payment intent.
* **Inputs**: `agent_id` (string), `max_single_amount` (positive integer in minor units, e.g. 1000000 for ₹10,000.00).
* **Main Flow**:
  1. User configures `max_single_amount` for agent in dashboard.
  2. System persists rule in database and caches policy object in Redis.
  3. When intent is submitted, AGENTGUARD compares `intent.amount` against `max_single_amount`.
  4. If `intent.amount <= max_single_amount`, rule check passes (`PASS`).
  5. If `intent.amount > max_single_amount`, rule check fails (`FAIL`) and decision outputs `BLOCK`.
* **Business Rules**: `BR-003`, `BR-005`.
* **State Changes**: Policy rules updated in DB and Redis cache.
* **Outputs**: Policy Check Result (`PASS` / `FAIL`), reason code `ERR_SINGLE_LIMIT_EXCEEDED`.
* **Error Conditions**: `ERR_SINGLE_LIMIT_EXCEEDED`, `ERR_INVALID_AMOUNT_FORMAT`.
* **Audit Events**: `EVENT_POLICY_UPDATED`, `EVENT_POLICY_LIMIT_EXCEEDED`.
* **Acceptance Criteria**: `AC-POLICY-001`.
* **Dependencies**: `FR-AGENT-001`.

---

### FR-POLICY-002: Category Restriction Setup & Enforcement
* **FR ID**: `FR-POLICY-002`
* **Title**: Category Whitelist/Blacklist Setup & MCC Enforcement
* **Source**: `REQ-POLICY-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`) / AGENTGUARD
* **Goal**: Restrict agent transactions by Merchant Category Code (MCC) or category tags.
* **Preconditions**: User is authenticated; policy object exists.
* **Trigger**: User configures category rules OR AGENTGUARD evaluates incoming payment intent.
* **Inputs**: `agent_id` (string), `allowed_categories` (array), `blocked_categories` (array).
* **Main Flow**:
  1. User selects allowed categories (e.g. "Electronics", "Office Supplies") and blocked categories (e.g. "Gambling", "Adult", "Crypto").
  2. System persists category rule set.
  3. AGENTGUARD evaluates `intent.category`.
  4. If category is in `blocked_categories`, AGENTGUARD outputs decision `BLOCK`.
  5. If category is in `allowed_categories`, rule check passes (`PASS`).
* **Business Rules**: `BR-003`, `BR-005`.
* **State Changes**: Category rules persisted.
* **Outputs**: Category Check Result (`PASS` / `FAIL`), reason code `ERR_CATEGORY_BLOCKED`.
* **Audit Events**: `EVENT_CATEGORY_BLOCKED`.
* **Acceptance Criteria**: `AC-POLICY-002`.
* **Dependencies**: `FR-AGENT-001`.

---

### FR-POLICY-003: Auto-Approval Threshold Setup & Escalation Rule
* **FR ID**: `FR-POLICY-003`
* **Title**: Auto-Approval Ceiling Configuration & Escalation Rule
* **Source**: `REQ-POLICY-003`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`) / AGENTGUARD
* **Goal**: Establish spending ceiling determining autonomous auto-approval versus human review escalation.
* **Preconditions**: User policy exists.
* **Trigger**: AGENTGUARD evaluates intent after basic policy checks pass.
* **Inputs**: `auto_approval_threshold` (integer, e.g. 500000 for ₹5,000.00).
* **Main Flow**:
  1. AGENTGUARD compares `intent.amount` against `auto_approval_threshold`.
  2. If `intent.amount <= auto_approval_threshold` and risk is low, decision outputs `ALLOW`.
  3. If `intent.amount > auto_approval_threshold` and amount $\le$ `max_single_amount`, decision outputs `REVIEW`.
* **Business Rules**: `BR-003`, `BR-006`.
* **Outputs**: Decision Output (`ALLOW` / `REVIEW`).
* **Audit Events**: `EVENT_INTENT_ESCALATED_TO_REVIEW`.
* **Acceptance Criteria**: `AC-POLICY-003`.
* **Dependencies**: `FR-POLICY-001`.
