# AGENTPAY
> **AI-Native Autonomous Commerce with Bounded, Explainable & Secure Payments**

### Give AI the ability to act — without giving AI unlimited financial power.

[![Razorpay AI Buildathon](https://img.shields.io/badge/Razorpay_AI_Buildathon-2026-blue.svg?style=for-the-badge&logo=razorpay)](https://razorpay.com)
[![Build Status](https://img.shields.io/badge/Build-PASSING-emerald.svg?style=for-the-badge)](https://github.com/Dharshan-05/AGENTPAY)
[![TypeScript](https://img.shields.io/badge/TypeScript-0_Errors-blue.svg?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000.svg?style=for-the-badge&logo=nextdotjs)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

**AGENTPAY** is a governed AI commerce and payment platform where an AI buyer can discover products, make purchasing decisions within explicit spending boundaries, pass policy and fraud controls, obtain human approval when required, and complete payments through Razorpay with a traceable audit trail.

Unlike traditional chatbots that simply hand off users to external checkout links, AGENTPAY establishes a **governed payment authority framework**. Financial autonomy is bounded by **AgentGuard** policy governance, evaluated by **FraudGuard** machine learning risk detection, explained using **SHAP explainable AI**, supervised by **Human-in-the-Loop (HITL)** escalations, and executed through server-validated **Razorpay payment rails**.


---

## 🏆 Built for Razorpay AI Buildathon

**Track:** *AI Growth & Agentic Commerce*

Traditional e-commerce relies on human-driven navigation. Conversational AI introduces shopping assistants, but they stop at recommendations or hand off control to standard payment pages. AGENTPAY bridges this gap by creating a **secure decision and execution plane** for autonomous commerce.

### Traditional Commerce vs. Agentic Commerce in AGENTPAY

```
TRADITIONAL COMMERCE:
User  ──►  Search Bar  ──►  Product Page  ──►  Cart  ──►  Payment Gateway  ──►  Order

AGENTIC COMMERCE (AGENTPAY):
User Request
   │
   ▼
Intent Engine (Product Search / Comparison / Purchase Request / Greeting Protection)
   │
   ▼
Product Discovery & Selection Lock (Provider-Agnostic Model)
   │
   ▼
Price Revalidation & Inventory Check (Server-Side Total Integrity)
   │
   ▼
Agent Identity Verification (Tenant & Agent Context Isolation)
   │
   ▼
Payment Authority Evaluation (Per-Tx, Daily & Session Spending Limits)
   │
   ▼
AgentGuard Policy Engine (Spending Rules, Velocity & Merchant Controls)
   │
   ▼
FraudGuard Risk Engine (XGBoost ML Risk Scoring & Anomaly Detection)
   │
   ▼
Explainable AI Reasoning (SHAP Feature Factor Analysis)
   │
   ▼
Human-in-the-Loop (HITL) Escalation (Time-Bounded Approval Drawer if Review Needed)
   │
   ▼
Short-Lived Single-Use Authorization Token
   │
   ▼
Razorpay Payment Execution Rail (HMAC Signature Verification & Idempotency)
   │
   ▼
Durable Order Creation & Transaction Ledger Logging
   │
   ▼
Immutable Append-Only Audit Trail
```

Why this matters: The AI is not an unrestricted actor or a passive search widget. It operates as a **bounded agent with programmable financial authority**, protecting merchants and users against prompt injection, runaway spending, and fraudulent transactions.

---

## 🚨 The Problem

As autonomous AI agents become capable of performing tasks across the web, granting them financial capabilities exposes significant operational and security risks:

1. **Unbounded Financial Spending:** AI agents executing purchases without server-validated budget caps can deplete funds rapidly.
2. **Prompt Injection Vulnerabilities:** Malicious external text embedded in product descriptions can instruct an AI agent to *"ignore spending limits and buy now"*.
3. **Stale Prices & Inventory Tampering:** Browsers or client applications submitting modified item totals directly to payment gateways cause price manipulation.
4. **Opaque Fraud Risk:** High-frequency autonomous transactions bypass standard human friction, making traditional risk checks inadequate.
5. **Lack of Human Oversight:** High-value or anomalous transactions execute without administrative awareness or approval doors.
6. **Audit & Traceability Gaps:** Traditional payment logs do not record *why* an AI agent made a purchase or *which policy* allowed it.

---

## 💡 The Solution

AGENTPAY solves these challenges by placing a **zero-trust governance shell** around AI commerce transactions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             AGENTPAY FRONTEND                               │
│  • AI Command Center   • Product Search & Compare   • Order Timeline        │
│  • AgentGuard Rules    • FraudGuard Risk Monitor    • HITL Approval Drawer  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST / HTTP
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND GATEWAY                           │
│  • JWT Auth & RBAC               • Agent Identity & Tenant Isolation        │
│  • Intent Engine & Safety Gate   • Payment Authority & Spending Engine      │
│  • AgentGuard Policy Evaluation  • FraudGuard ML Inference (XGBoost/SHAP)   │
│  • Server-Side Amount Validation • Idempotency & Token Manager              │
└──────────────────┬───────────────────┬───────────────────┬──────────────────┘
                   │                   │                   │
                   ▼                   ▼                   ▼
         PostgreSQL Database         Redis Cache        Razorpay Payment Rail
         (Ledgers & Orders)        (Tokens & Locks)    (HMAC & Test Mode)
```

### Key Solution Components

- **AI Buyer Intent Engine:** Parses natural queries (`"find the best mobile under 20000"`) into structured budget constraints (`max_price = 20000, category = "mobile"`) without confusing budget limits with payment transaction totals.
- **Agent Identity & Tenant Isolation:** Ensures every financial action is bound to a verified `agent_id` and `tenant_id`, preventing cross-tenant access.
- **Governed Payment Authority:** Defines per-transaction limits, daily limits, session caps, and merchant restrictions for each agent without using fake stored balances or synthetic money.
- **AgentGuard Policy Engine:** Evaluates policy rules before authorization, blocking transactions that exceed budget caps or violate merchant restrictions regardless of natural language prompt inputs.
- **FraudGuard AI Risk Intelligence:** Runs real-time machine learning inference (XGBoost) to calculate transaction risk scores (0.0 to 1.0) and anomaly probability.
- **SHAP Explainable AI (XAI):** Generates human-readable risk explanations detailing the positive and negative risk factors behind every decision.
- **Human-in-the-Loop (HITL):** Automatically pauses transactions flagged for review, presenting an operator drawer (`[VERIFY & CONTINUE PAYMENT]`) with single-use, time-bounded approval tokens.
- **Razorpay Execution Rail:** Creates Razorpay payment orders server-side, verifies HMAC signatures, and guarantees exact payment amount integrity.
- **Immutable Audit Trail:** Records chained append-only telemetry events (`INTENT_CREATED`, `AGENTGUARD_EVALUATED`, `FRAUDGUARD_EVALUATED`, `PAYMENT_VERIFIED`, `ORDER_CREATED`).

---

## 🔐 Why AGENTPAY? (Core Differentiator)

> **"AGENTPAY does not give AI unlimited financial power — AGENTPAY gives AI bounded financial authority."**

$$\text{Financial Security} = \text{AI Intent} + \text{Agent Identity} + \text{AgentGuard Policy} + \text{FraudGuard ML} + \text{Human Oversight} + \text{Razorpay Rail} + \text{Auditability}$$

- **Policy-First:** AgentGuard rules cannot be bypassed by prompt injection attacks.
- **Truthful Status:** Surfaces `PRODUCT_PROVIDER_CONFIGURATION_REQUIRED` and `FULFILLMENT_UNAVAILABLE` honestly when live third-party provider credentials are unconfigured.
- **Server-Authoritative:** Payment amounts are calculated server-side from catalog data; client-submitted totals are strictly validated and rejected if modified.
- **Zero Secret Exposure:** `RAZORPAY_SECRET`, `OPENROUTER_API_KEY`, and database credentials remain strictly server-side.

---

## 📊 Feature Matrix

| Capability | What AGENTPAY Does | Status |
| :--- | :--- | :--- |
| **AI Buyer Intent Engine** | Parses natural language requests (`"best mobile under 20000"`), extracts budget constraints, and enforces greeting safety protection (`HI`/`HELLO`). | **PASS** |
| **Product Discovery Abstraction** | Provider-independent normalized product model (`title`, `price`, `currency`, `rating`, `specs`, `risk_score`). | **PASS** |
| **Product Comparison Engine** | Multi-attribute spec, price, rating, and risk comparison (`BEST VALUE`, `LOWEST PRICE`). | **PASS** |
| **Price & Inventory Revalidation** | Revalidates item prices and stock availability immediately before checkout; surfaces `PRICE_CHANGED` if total differs. | **PASS** |
| **Agent Identity & Isolation** | Enforces `agent_id` and `tenant_id` context on all operations, preventing cross-tenant or cross-agent data leaks. | **PASS** |
| **Governed Payment Authority** | Configures per-transaction limits, daily limits, session caps, and merchant restrictions for autonomous agents. | **PASS** |
| **AgentGuard Policy Governance** | Evaluates policy rules before payment authorization; blocks transactions exceeding spending caps or velocity limits. | **PASS** |
| **FraudGuard ML Risk Engine** | Real-time XGBoost risk scoring (0.0 to 1.0) and anomaly detection across transaction features. | **PASS** |
| **SHAP Explainable AI (XAI)** | Generates feature-level risk explanations detailing why a transaction was approved, reviewed, or blocked. | **PASS** |
| **Human-in-the-Loop (HITL)** | Escalates review-required transactions to operator drawer (`[VERIFY & CONTINUE PAYMENT]`) with time-limited tokens. | **PASS** |
| **Short-Lived Authorization** | Single-use, short-lived authorization tokens bound to exact product IDs, merchants, and server totals. | **PASS** |
| **Payment Amount Integrity** | Server calculates exact total (`unit_price * quantity + tax + shipping - discount`); rejects browser amount tampering. | **PASS** |
| **Razorpay Payment Rail** | Server-side Razorpay order creation, client checkout modal, HMAC signature verification, and test mode execution. | **PASS** |
| **Order State Machine** | Manages explicit lifecycle states: `DRAFT` → `AUTHORIZED` → `PAYMENT_SUCCESS` → `ORDER_CONFIRMED` → `FULFILLMENT_UNAVAILABLE`. | **PASS** |
| **Idempotency Protection** | Idempotency keys protect authorization, payment verification, order creation, and refunds against duplicate retries. | **PASS** |
| **Immutable Audit Trail** | Chained append-only audit event logging for all financial decisions and state transitions. | **PASS** |
| **Prompt Injection Defense** | Treats external product catalog descriptions as untrusted data; neutralizes malicious prompt instructions. | **PASS** |
| **Live Retail Catalog Connectivity** | Provider-independent discovery architecture for live third-party merchant catalog APIs. | **PASS WITH CONFIGURATION REQUIRED** |
| **Live Order Fulfillment Sync** | Third-party merchant order submission and shipment tracking synchronization. | **PASS WITH CONFIGURATION REQUIRED** |

---

## 🔄 End-to-End Agentic Commerce Flow

```mermaid
flowchart TD
    A[User Request: 'Find best phone under ₹20,000'] --> B[Intent Engine: Parse Category & Budget Limit]
    B --> C[Product Discovery Abstraction]
    C --> D[Product Comparison & Recommendation]
    D --> E[User Product Selection Lock]
    E --> F[Server-Side Price Revalidation]
    F --> G[Inventory Availability Revalidation]
    G --> H[Agent Identity & Tenant Verification]
    H --> I[Payment Authority Limit Check]
    I --> J[AgentGuard Policy Engine Evaluation]
    J -->|Allowed| K[FraudGuard ML Risk Scoring]
    J -->|Denied| X[Block Transaction & Log Policy Denial]
    K --> L[SHAP Explainable Risk Factor Analysis]
    L --> M{Risk Threshold Evaluation}
    M -->|Low Risk: <0.30| N[Issue Short-Lived Single-Use Auth Token]
    M -->|Medium Risk: 0.30 - 0.70| O[HITL Escalation Drawer]
    M -->|High Risk: >0.70| Y[Block Transaction & Log Fraud Alert]
    O -->|Operator Approved| N
    O -->|Operator Denied| Z[Reject Transaction & Expire Token]
    N --> P[Create Server-Side Razorpay Order]
    P --> Q[Execute Razorpay Checkout Modal]
    Q --> R[Backend Signature & HMAC Verification]
    R --> S[Create Durable Order Record AG_ORD_XXX]
    S --> T[Commit Inventory & Record Immutable Audit Event]
```

---

## 🛡️ AgentGuard — Policy Enforcement

**AgentGuard** answers the primary question: **"Is this action allowed by policy?"**

```json
{
  "agent_id": "ag_01h9x8y7z6",
  "tenant_id": "tenant_enterprise_01",
  "policy_evaluation": {
    "per_transaction_limit": 25000.00,
    "requested_amount": 19999.00,
    "daily_budget_remaining": 45000.00,
    "merchant_status": "ALLOWED",
    "category_status": "ALLOWED",
    "decision": "ALLOW",
    "reason": "Transaction amount INR 19,999.00 is within per-transaction limit (INR 25,000.00) and daily limit."
  }
}
```

- **Spending Limits:** Enforces per-transaction caps, daily spending budgets, monthly limits, and velocity thresholds.
- **Merchant & Category Controls:** Restricts agent purchasing to approved merchant registries and categories.
- **Hard Policy Boundaries:** Natural language prompt instructions embedded in external content cannot override server-side policy code.

---

## 🧠 FraudGuard — AI Risk Intelligence

**FraudGuard** answers the critical question: **"Does this transaction look anomalous or risky?"**

```
FraudGuard Risk Inference:
┌─────────────────────────────────────────────────────────────┐
│ Model: XGBoost Classifier v2.1 (Trained on SMOTE Features) │
│ Risk Score: 0.082 (LOW RISK)                               │
│ Risk Level: ALLOW                                           │
└─────────────────────────────────────────────────────────────┘
```

- **Machine Learning Architecture:** XGBoost classification model trained on engineered transaction features including velocity, amount deviations, time-of-day anomalies, merchant risk ratings, and agent history.
- **Synthetic Balancing (SMOTE):** Handles class imbalance during training to detect rare fraud patterns effectively.
- **Deterministic Risk Matrix:**
  - `Risk Score < 0.30`: **ALLOW** (Automatic Authorization)
  - `0.30 <= Risk Score <= 0.70`: **REVIEW** (Escalate to HITL Approval Drawer)
  - `Risk Score > 0.70`: **BLOCK** (Automatic Hard Block)

---

## 🔎 Explainable AI (XAI & SHAP)

Rather than returning an opaque boolean verdict, AGENTPAY computes **SHAP (SHapley Additive exPlanations) values** for every risk inference to provide full transparency.

```
┌─────────────────────────────────────────────────────────────┐
│ FRAUDGUARD XAI RISK EXPLANATION                             │
├─────────────────────────────────────────────────────────────┤
│ Transaction ID: tx_88f9a2b4  ·  Risk Score: 0.08 (LOW RISK)│
│                                                             │
│ Risk Factor Contributions:                                  │
│  [+] Known Merchant ID (Amazon)      -0.14  (Decreases Risk)│
│  [+] Within Historical Velocity Limit-0.09  (Decreases Risk)│
│  [+] Agent Spend History Verified    -0.06  (Decreases Risk)│
│  [-] IP Geolocation Soft Deviation   +0.03  (Increases Risk)│
│                                                             │
│ Explanation Summary:                                        │
│ Transaction displays strong legitimacy signals matching      │
│ baseline agent behavior.                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 👤 Human-in-the-Loop (HITL)

AGENTPAY is **autonomous within explicit boundaries**, not blindly autonomous. When AgentGuard policy rules or FraudGuard risk scores indicate ambiguity or elevated risk, the system triggers a **Human-in-the-Loop escalation**.

```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ HUMAN-IN-THE-LOOP APPROVAL REQUIRED                      │
├─────────────────────────────────────────────────────────────┤
│ Agent:        ProcurementBot-v4                             │
│ Product:      Dell UltraSharp 32" 4K Monitor                │
│ Total Amount: ₹68,500.00                                    │
│ Policy:       EXCEEDS_AUTO_THRESHOLD (Limit: ₹50,000.00)   │
│ Risk Score:   0.42 (MEDIUM RISK - Velocity Anomaly)         │
│ Expiry:       04m 58s remaining                             │
│                                                             │
│ [ DENY TRANSACTION ]            [ VERIFY & CONTINUE PAYMENT ]
└─────────────────────────────────────────────────────────────┘
```

- **Time-Bounded Tokens:** HITL approval requests expire automatically after a configurable window (e.g., 5 minutes).
- **Single-Use Verification:** Once an operator approves a request, the issued token is consumed immediately and cannot be reused.
- **Amount & Merchant Locking:** An approval for ₹68,500 cannot be reused to pay ₹685,000 or pay a different merchant.

---

## 🔒 Security Architecture

AGENTPAY implements defense-in-depth security across all application layers:

1. **Zero Secret Exposure:** All credentials (`RAZORPAY_SECRET`, `OPENROUTER_API_KEY`, database secrets) remain strictly server-side.
2. **JWT Authentication & RBAC:** Multi-tenant JWT session handling with role-based access control (`SUPER_ADMIN`, `RISK_ANALYST`, `COMPLIANCE`, `DEVELOPER`).
3. **Tenant & Agent Isolation:** All database queries enforce `tenant_id` and `agent_id` filters.
4. **Prompt Injection Defense:** External catalog descriptions are treated as untrusted data strings and sanitized.
5. **Payment Amount Integrity:** Server calculates final totals (`unit_price * qty + tax + shipping - discount`); client amount tampering triggers automatic blocks.
6. **HMAC Webhook Verification:** Razorpay webhook payloads are verified using SHA-256 HMAC signatures.

---

## 💳 Razorpay Integration

AGENTPAY uses **Razorpay** as its authoritative payment execution rail while providing the AI decision and governance wrapper.

```
AI Buyer Selection ──► AgentGuard & FraudGuard ──► Single-Use Token ──► Razorpay Order Creation
                                                                                 │
                                                                                 ▼
Order Confirmed ◄── HMAC Verification ◄── Razorpay Signature ◄── Razorpay Test Checkout
```

### Razorpay Integration Highlights
- **Server-Side Order Creation:** Payment orders are created via Razorpay REST APIs using server-stored key credentials.
- **Razorpay Checkout Modal:** Renders Razorpay's native checkout UI for seamless test-mode card/UPI payments.
- **Signature Verification:** Verifies `razorpay_payment_id`, `razorpay_order_id`, and `razorpay_signature` using server HMAC calculation.
- **Idempotency:** Payment verification endpoints use unique idempotency keys to prevent duplicate order generation.

---

## 🛒 Commerce Engine & Order State Machine

AGENTPAY maintains a deterministic order state machine to track order lifecycles transparently:

```
[DRAFT] ──► [AUTHORIZED] ──► [PAYMENT_PENDING] ──► [PAYMENT_SUCCESS] ──► [ORDER_CONFIRMED]
                                                           │
                                                           ▼
                                               [FULFILLMENT_UNAVAILABLE]*
                                        (*Surfaced honestly when live retail 
                                          provider API keys are unconfigured)
```

---

## ⚡ Transaction Safety & Idempotency

- **Idempotency Keys:** Every authorization, payment verification, and order creation request includes a unique idempotency key (`Idempotency-Key: ik_xxxxxxxx`).
- **Concurrent Locking:** Database row locking prevents double-spending when an agent sends duplicate concurrent purchase requests.
- **Replay Protection:** Authorization tokens and Razorpay payment signatures are invalidated upon first consumption.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[Next.js Frontend Client :3000] -->|HTTPS / REST| Gateway[FastAPI Backend Gateway :8000]
    Gateway --> Auth[JWT Auth & RBAC Middleware]
    Gateway --> Intent[AI Buyer Intent Engine]
    Gateway --> AgentGuard[AgentGuard Policy Service]
    Gateway --> FraudGuard[FraudGuard ML Risk Engine]
    Gateway --> Commerce[Commerce & Order Facade]
    
    AgentGuard --> DB[(PostgreSQL Database)]
    FraudGuard --> ML[XGBoost & SHAP Inference]
    Commerce --> DB
    Commerce --> Redis[(Redis Cache / Locks)]
    Commerce -->|Server API| Razorpay[Razorpay Payment API]
```

---

## 🧰 Tech Stack

### Frontend Control Plane
- **Framework:** Next.js 14.2 (App Router)
- **Language:** TypeScript (Strict Type Safety - 0 Errors)
- **Styling:** Tailwind CSS, Glassmorphism, Neon AGENTPAY Visual System
- **Icons & Animation:** Lucide React, Framer Motion
- **State & Data:** Shared Commerce Store, Custom DOM Event Synchronizer

### Backend API & Agent Runtime
- **Framework:** Python 3.11, FastAPI 0.110
- **Database & ORM:** PostgreSQL, SQLAlchemy 2.0, Alembic Migrations
- **Caching & Locks:** Redis 7.2
- **Validation:** Pydantic v2
- **Testing:** pytest 9.1, asyncio test suite

### AI & Machine Learning
- **Model Framework:** Scikit-learn, XGBoost Classifier
- **Explainable AI:** SHAP (SHapley Additive exPlanations)
- **Data Processing:** NumPy, Pandas

### Payment & Infrastructure
- **Payment Gateway:** Razorpay Test Mode API & SDK
- **Containerization:** Docker, Docker Compose
- **E2E Automation Audit:** Playwright Chromium Test Suite

---

## 📁 Project Structure

```
AGENTPAY/
├── frontend/                     # Next.js 14 Frontend Application
│   ├── app/                      # App Router Routes
│   │   ├── ai-command-center/   # AI Buyer Interface & Conversational Engine
│   │   ├── command-center/      # Operations Command Center
│   │   ├── checkout/            # HITL Checkout & Razorpay Integration
│   │   ├── orders/              # Order History & Tracking Drawer
│   │   ├── login/               # Zero-Trust Auth & Persona Login
│   │   ├── products/            # Product Search & Comparison
│   │   ├── agentguard/          # AgentGuard Policy Management
│   │   ├── fraudguard/          # FraudGuard Risk Monitoring
│   │   └── ...                  # Additional Operational Dashboards
│   ├── components/              # Shared UI & Layout Components
│   │   ├── layout/              # AppShell, AgentPaySidebar, TopNav
│   │   └── ...                  # Dashboard Widgets
│   └── lib/                     # Commerce Store & Hooks
├── backend/                      # FastAPI Backend & Agent Runtime
│   ├── apps/agent-runtime/
│   │   ├── app/
│   │   │   ├── api/v1/          # REST Routers (commerce, agents, auth, etc.)
│   │   │   ├── commerce/        # Product, Order & Fulfillment Services
│   │   │   ├── domain/          # Entities & Schemas
│   │   │   └── main.py          # FastAPI Application Entrypoint
│   │   └── tests/commerce/      # Backend Pytest Test Suite
│   ├── alembic/                 # Database Migrations
│   └── docker-compose.yml       # Production Stack Orchestration
└── README.md                     # Master Documentation
```

---

## 🎨 Frontend Experience

The AGENTPAY frontend provides an enterprise dark fintech interface designed for AI agent governance:

- **AI Command Center (`/ai-command-center`):** Interactive conversational AI buyer for product discovery, budget-constrained search, and natural language comparison.
- **Login & Authentication (`/login`):** Zero-Trust access page with demo persona presets, email/password fields, show/hide password controls, and remember session support.
- **Command Center (`/command-center`):** Unified operational dashboard surfacing real-time telemetry, transaction velocity, active agents, and risk metrics.
- **AgentGuard Policies (`/agentguard`):** Configure spending caps, daily budgets, merchant whitelists, and velocity rules for AI agents.
- **FraudGuard Risk Monitor (`/fraudguard`):** View real-time ML risk scores, anomaly signals, and SHAP factor explanations.
- **Checkout & HITL Approval (`/checkout`):** Review purchase authorizations, view decision breakdowns, execute Razorpay payments, or approve review-required transactions.
- **Orders & Tracking (`/orders`):** Order history timeline with detailed drawer popups surfacing transaction ledgers and fulfillment status.

---

## 🔌 Backend Capabilities (FastAPI OpenAPI)

The backend provides full REST API coverage documented interactively at `http://localhost:8000/docs`:

- `POST /api/v1/commerce/search` — Budget-constrained product discovery
- `POST /api/v1/commerce/compare` — Multi-attribute product comparison
- `POST /api/v1/commerce/decision/evaluate` — AgentGuard & FraudGuard evaluation
- `POST /api/v1/commerce/decision/authorize` — Short-lived authorization token issuance
- `POST /api/v1/commerce/razorpay/create-order` — Server-side Razorpay order creation
- `POST /api/v1/commerce/razorpay/verify-payment` — HMAC signature verification & order placement
- `GET  /api/v1/commerce/orders` — Order history and ledger retrieval
- `GET  /api/v1/commerce/health` — Subsystem health and provider readiness status

---

## 🚀 Getting Started

### Prerequisites
- **Node.js:** v18.0.0 or higher
- **Python:** v3.11.0 or higher
- **Git:** Installed on local system

### Quick Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Dharshan-05/AGENTPAY.git
cd AGENTPAY
```

#### 2. Start Backend Service
```bash
cd backend/apps/agent-runtime
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### 3. Start Frontend Service
```bash
cd ../../../frontend
npm install
npm run dev
```

Open your browser at **`http://localhost:3000`**.

---

## 🔑 Environment Configuration

Create a `.env` file in `backend/apps/agent-runtime` (or use `.env.example`):

```env
# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Backend Gateway
HOST=127.0.0.1
PORT=8000

# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agentpay

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Razorpay Test Credentials (Server-Side Only)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key

# OpenRouter / LLM API Key (Server-Side Only)
OPENROUTER_API_KEY=your_openrouter_api_key

# Security Secrets
JWT_SECRET_KEY=your_super_secret_jwt_key_here
```

*Note: Never commit your `.env` file or credentials to Git.*

---

## 🧪 Testing & Quality Audit

The codebase maintains rigorous quality and testing baselines:

- **Frontend Static Analysis:** `npx tsc --noEmit` — **0 Errors (Exit Code 0)**
- **Backend Commerce Unit Suite:** `pytest tests/commerce/` — **16/16 Passed in 15.64s**
- **Playwright E2E Master Audit:** `master_universal_browser_audit.py` — **1,044 Controls Tested, 1,032 PASS, 0 Failures, 0 Console Errors, 0 Network Errors (Verdict: PASS)**

---

## ⚠️ Current Limitations

To maintain absolute transparency for hackathon evaluation:

- **Live Retail Catalog API Configuration:** Live third-party merchant credentials (e.g. Amazon SP-API / Flipkart Marketplace API) are currently unconfigured in standard test mode. When unconfigured, the system surfaces `PRODUCT_PROVIDER_CONFIGURATION_REQUIRED` and `FULFILLMENT_UNAVAILABLE` honestly rather than generating fake shipment numbers or synthetic delivery dates.
- **Razorpay Integration Mode:** Operating in Razorpay Test Mode with test keys. Real-money capture requires production Razorpay merchant activation.

---

## 🎬 Demo Scenario

1. **User Prompt:** User opens `/ai-command-center` and asks: *"find the best mobile under 20000"*.
2. **Intent Parsing:** The AI intent engine parses `max_price = 20000, category = "mobile"`.
3. **Product Discovery:** Normalized product catalog entities are retrieved and displayed in AGENTPAY cards.
4. **Comparison:** User requests *"compare the first two"*, triggering multi-attribute spec, rating, and price evaluation.
5. **Product Selection & Revalidation:** User selects a product. Server revalidates price integrity and inventory stock.
6. **Governance Check:** Agent Identity (`agent_id`) is verified. **AgentGuard** verifies spending caps.
7. **Risk Assessment:** **FraudGuard ML** calculates risk score (e.g. `0.082 - LOW RISK`). **SHAP** generates risk explanations.
8. **Authorization Token:** System issues a single-use, 5-minute authorization token.
9. **Razorpay Payment:** User navigates to checkout, triggering server-side Razorpay order creation and native test checkout modal.
10. **Order Confirmation:** Backend verifies HMAC signature, commits inventory, creates order `AG_ORD_XXXXXXXX`, and logs an immutable audit event.

---

## 🌟 Unique Selling Proposition (USP)

> **"AGENTPAY turns autonomous AI commerce from an unrestricted action-taking risk into a governed financial execution system."**

| Dimension | Traditional Chatbot | AI Shopping Assistant | AGENTPAY |
| :--- | :--- | :--- | :--- |
| **Intent Processing** | Text Search | Product Advice | Budget & Safety Intent Parsing |
| **Product Discovery** | Single Link | Recommendation List | Provider-Agnostic Model |
| **Financial Authority** | None (User Pays) | External Redirect | Bounded Server-Enforced Authority |
| **Policy Enforcement** | None | None | Server-Side AgentGuard Rules |
| **Fraud Risk Intelligence** | None | None | Real-Time XGBoost & SHAP XAI |
| **Human Oversight** | Manual | None | Time-Bounded HITL Approval Drawer |
| **Payment Rail** | Manual Redirect | External Handoff | Server-Validated Razorpay Execution |
| **Auditability** | None | Text History | Chained Immutable Event Ledger |

---

## 🔮 Future Scope & Roadmap

- **Multi-Merchant Live Connectors:** Deep integration with Amazon SP-API, Flipkart Marketplace API, and Shopify Admin API.
- **Voice Commerce Engine:** Real-time audio intent processing for hands-free autonomous ordering.
- **Graph Risk Networks:** Graph-based fraud detection to identify coordinated multi-agent attack rings.
- **Autonomous Agent-to-Agent Commerce:** Protocol specifications for AI agents to negotiate prices and trade services autonomously.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository (`https://github.com/Dharshan-05/AGENTPAY`).
2. Create a feature branch (`git checkout -b feature/governance-enhancement`).
3. Commit your changes (`git commit -m 'Add adaptive velocity policy rule'`).
4. Push to your branch (`git push origin feature/governance-enhancement`).
5. Open a Pull Request for review.

---

## 📜 License

This project is submitted for the **Razorpay AI Buildathon 2026**. License information will be updated upon official release.

