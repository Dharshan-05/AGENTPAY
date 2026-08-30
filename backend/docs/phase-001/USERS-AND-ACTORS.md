# AGENTPAY — Users & Actors

## 1. Actor Taxonomy

AGENTPAY categorizes system participants into five primary actors, spanning human users, autonomous software instances, external commercial entities, and system management personnel.

```
+-----------------------------------------------------------------------------------+
|                                  SYSTEM ACTORS                                    |
+-------------------+-------------------+-------------------+-----------------------+
|  HUMAN USER       |  AI AGENT         |  MERCHANT         |  ADMIN / ANALYSTS     |
|  (Owner)          |  (Initiator)      |  (Recipient)      |  (Operators)          |
+-------------------+-------------------+-------------------+-----------------------+
```

---

## 2. Actor Specifications

### 2.1 USER (Human Account Owner)
* **Definition**: The ultimate human financial owner who registers on AGENTPAY, creates and manages AI AGENT instances, configures policy rules, funds payments, and provides human-in-the-loop approvals.
* **Responsibilities**:
  * Authorizing AI AGENT registration and issuing cryptographic credentials.
  * Setting spending limits, category restrictions, and merchant rules.
  * Reviewing and approving/rejecting transaction escalations in the Approval Center.
  * Triggering Emergency Stop / Agent Revocation when needed.
* **Permissions**: `USER_ADMIN` (Full administrative rights over owned agents, policies, and transaction history).
* **Interface Access**: User Web Dashboard, Mobile Approval App, Notification Webhooks.
* **Security Boundaries**: Protected by Multi-Factor Authentication (MFA), passwordless webauthn/JWT tokens. Cannot inspect secrets of other users.

### 2.2 AI AGENT (Autonomous Initiator)
* **Definition**: An autonomous software service, LLM agent, or automated workflow operating on behalf of a USER to discover products, evaluate procurement choices, and initiate transaction requests.
* **Responsibilities**:
  * Authenticating with AGENTPAY using valid cryptographic signatures or HMAC API keys.
  * Constructing well-formed, idempotent `PAYMENT INTENT` payloads detailing amount, currency, merchant details, product category, and contextual metadata.
  * Listening for payment intent status updates (`PENDING_APPROVAL`, `AUTHORIZED`, `REJECTED`).
* **Permissions**: `AGENT_INITIATE` (Restricted strictly to intent creation and status queries within explicitly assigned policy boundaries).
* **Interface Access**: RESTful / gRPC Agent Gateway API.
* **Security Boundaries**: Cannot modify policy rules, cannot approve escalated transactions, cannot access human user payment credentials or raw bank tokens.

### 2.3 MERCHANT (Commercial Payee)
* **Definition**: The external vendor, merchant, or service provider receiving payment from an authorized transaction initiated by an AI AGENT.
* **Responsibilities**:
  * Providing verified merchant identity data (Domain, MID, MCC - Merchant Category Code).
  * Accepting payment settlement via underlying payment adapters (Razorpay / UPI / Bank Rails).
  * Returning transaction fulfillment receipts and status callbacks.
* **Permissions**: `MERCHANT_READ` (Querying transaction status and verification signals).
* **Interface Access**: Merchant Verification Webhooks / Payment Adapter Gateway APIs.
* **Security Boundaries**: Cannot view user policy rules, agent internal logic, or risk scoring parameters.

### 2.4 ADMIN / RISK OPERATOR (Platform Management)
* **Definition**: Platform operations personnel responsible for monitoring overall platform health, system-wide risk metrics, merchant integrity, and transaction processing telemetry.
* **Responsibilities**:
  * Monitoring aggregate fraud signals and system velocity.
  * Managing global risk model configurations and fallback policy sets.
  * Reviewing flagged high-risk system alerts.
* **Permissions**: `PLATFORM_ADMIN` / `RISK_OPERATOR` (Global read access over telemetry, aggregate metrics, and administrative system controls).
* **Interface Access**: Global Admin Dashboard & Operations Console.
* **Security Boundaries**: Subject to strict audit logging and role-based access control (RBAC). Cannot initiate transactions on behalf of users.

### 2.5 SECURITY / FRAUD ANALYST (Investigation Specialist)
* **Definition**: Specialized security analyst investigating suspicious transaction patterns, agent abuse attempts, prompt injection exploits leading to financial requests, and novel fraud vectors.
* **Responsibilities**:
  * Analyzing XAI decision traces and feature attribution breakdowns for flagged transactions.
  * Updating FraudGuard ML model feature sets and blacklists.
  * Conducting forensic audits over immutable audit trail logs.
* **Permissions**: `FRAUD_ANALYST` (Deep diagnostic read access to transaction risk traces, feature maps, and audit logs).
* **Interface Access**: FraudGuard Investigation Console & XAI Analytics Suite.
* **Security Boundaries**: Read-only access to sensitive historical data; cannot alter live user policy definitions directly without user consent.

---

## 3. Actor Interaction Matrix

| Initiating Actor | Target Component | Action | Authorization Level |
| :--- | :--- | :--- | :--- |
| **USER** | Agent Management | Register / Revoke Agent | Owner MFA Required |
| **USER** | AGENTGUARD | Set Spending Policy Rules | Owner Session |
| **USER** | Approval Center | Approve / Reject Intent | Owner Session + Step-up Auth |
| **AI AGENT** | Payment Intent API | Create `PAYMENT INTENT` | Signed HMAC / API Key |
| **AI AGENT** | Agent Gateway | Query Intent Status | Signed HMAC / API Key |
| **MERCHANT** | Payment Adapter | Process Settlement Payload | Webhook / API Signature |
| **FRAUD ANALYST**| FRAUDGUARD Console | Inspect XAI Decision Trace | Analyst Session + RBAC |
