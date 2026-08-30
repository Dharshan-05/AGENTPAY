# AGENTPAY — User Requirements

## 1. Overview

User requirements specify all capabilities, controls, and visual interfaces provided to the **Human Account Owner** (`USER`) within AGENTPAY. These requirements ensure that human oversight remains supreme over all autonomous agent activity.

---

## 2. Detailed Requirement Baseline

### 2.1 User Account & Authentication
* **REQ-USR-001**: The system shall require Multi-Factor Authentication (MFA) for user registration, login, and policy modifications.
* **REQ-USR-002**: The system shall support secure session management with automatic token expiration after 15 minutes of inactivity.
* **REQ-USR-003**: The system shall allow users to manage profile settings, notification preferences (Email, Webhook, SMS, In-App Push), and security credentials.

### 2.2 Agent Onboarding & Management
* **REQ-USR-004**: The system shall enable users to register new AI AGENT instances by defining an Agent Name, Functional Purpose, and assigned capabilities.
* **REQ-USR-005**: Upon agent registration, the system shall issue a unique `Agent ID` and generate a cryptographically secure 256-bit HMAC secret key displayed to the user exactly once.
* **REQ-USR-006**: The system shall allow users to view a list of all registered agents along with their real-time lifecycle status (`ACTIVE`, `PAUSED`, `SUSPENDED`, `REVOKED`).
* **REQ-USR-007**: The system shall allow users to manually pause or resume any owned AI AGENT at any time.

### 2.3 Policy & Governance Configuration
* **REQ-USR-008**: The system shall provide a visual policy configurator for setting single-transaction spending limits (e.g. Max ₹10,000) for each agent.
* **REQ-USR-009**: The system shall allow users to configure daily and monthly aggregate spending budgets per agent.
* **REQ-USR-010**: The system shall allow users to configure allowed and forbidden Merchant Category Codes (MCC) and merchant domain whitelists/blacklists.
* **REQ-USR-011**: The system shall allow users to set a custom Auto-Approval Threshold (e.g. Auto-approve intents $\le$ ₹5,000 if policy compliant and low risk).
* **REQ-USR-012**: The system shall allow users to configure temporal rules (e.g. operating hours window between 09:00 AM and 09:00 PM IST).

### 2.4 Human-in-the-Loop Approval Workflows
* **REQ-USR-013**: The system shall present pending transaction escalations in a dedicated real-time "Approval Center" UI.
* **REQ-USR-014**: For every pending approval request, the UI shall display the agent identity, merchant name, transaction amount, computed `RISK SCORE`, top risk factors, and the XAI natural language explanation.
* **REQ-USR-015**: The system shall provide single-click "Approve" and "Reject" action controls for pending approval requests.
* **REQ-USR-016**: The system shall enforce a configurable expiration timeout (default: 15 minutes) for pending human approval requests; if unacted upon, the transaction automatically defaults to `REJECTED`.

### 2.5 Emergency Controls & Safety
* **REQ-USR-017**: The system shall feature a prominent global "EMERGENCY STOP" button on the dashboard UI.
* **REQ-USR-018**: Triggering the Emergency Stop shall immediately transition all agents owned by the user to `SUSPENDED` status, purge authentication caches, and cancel all pending transactions.
* **REQ-USR-019**: The system shall allow users to permanently revoke an agent's credentials, changing its state to `REVOKED`.

### 2.6 Dashboard & Audit Exploration
* **REQ-USR-020**: The system shall provide a real-time dashboard displaying active agents, total spending metrics, policy enforcement stats, and a live transaction activity feed.
* **REQ-USR-021**: The system shall allow users to search, filter, and inspect detailed immutable audit log records for past transactions.
