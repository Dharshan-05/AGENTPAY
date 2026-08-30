# AGENTPAY — User Journeys

## Journey 1: Agent Onboarding & Policy Setup

### Actor: USER (Human Account Owner)

```
1. USER logs into AGENTPAY Web Dashboard via MFA.
2. USER navigates to "Agent Management" -> clicks "Register New AI Agent".
3. USER fills registration metadata:
   - Name: "Procurement Bot Alpha"
   - Purpose: "Automated office hardware & electronics purchasing"
4. System generates:
   - Agent ID: agt_98a12c44
   - HMAC API Secret Key (displayed once to USER)
5. USER opens AGENTGUARD Policy Configurator and sets spending controls:
   - Per-transaction Limit: ₹10,000
   - Daily Limit: ₹25,000
   - Allowed Categories: "Electronics", "Office Supplies"
   - Blocked Categories: "Gambling", "Adult", "Crypto"
   - Auto-Approval Threshold: ₹5,000 (Transactions <= ₹5,000 auto-approve if compliant)
6. System activates agent state to ACTIVE and saves immutable policy baseline.
```

---

## Journey 2: Autonomous Agent Transaction — Instant Auto-Approval

### Actors: AI AGENT, AGENTGUARD, FRAUDGUARD, PAYMENT GATEWAY

```
1. AI AGENT finds required hardware at "Trusted Electronics Store" for ₹2,500.
2. AI AGENT constructs PAYMENT INTENT payload signed with HMAC API key:
   - Amount: ₹2,500
   - Merchant: "Trusted Electronics Store" (Domain: trusted-elec.com, MCC: 5732)
   - Category: "Electronics"
3. AGENTGUARD evaluates:
   - HMAC Signature: VALID
   - Agent Status: ACTIVE
   - Transaction Amount (₹2,500) <= Single Limit (₹10,000): PASS
   - Category ("Electronics"): ALLOWED
   - Auto-approve Threshold (₹5,000): ELIGIBLE FOR AUTO-APPROVE
4. FRAUDGUARD scores transaction:
   - Amount Anomaly: Normal
   - Merchant Trust Score: 95/100
   - Computed RISK SCORE: 12/100 (LOW RISK)
5. XAI ENGINE generates rationale:
   - "Transaction approved. Amount ₹2,500 is within auto-approval threshold ₹5,000. Category 'Electronics' is explicitly allowed. Merchant trust is high (95/100)."
6. System renders decision: ALLOW.
7. Payment executes successfully via Payment Gateway Adapter.
8. Dashboard & Audit Trail update immediately with execution receipt.
```

---

## Journey 3: High-Value Transaction Escalation & Human Approval

### Actors: AI AGENT, AGENTGUARD, FRAUDGUARD, USER (Human Approver)

```
1. AI AGENT attempts to purchase server equipment for ₹8,500.
2. AI AGENT submits signed PAYMENT INTENT payload:
   - Amount: ₹8,500
   - Merchant: "Enterprise Server Direct"
   - Category: "Electronics"
3. AGENTGUARD evaluates:
   - Single Limit Check (₹8,500 <= ₹10,000): PASS
   - Category Check ("Electronics"): ALLOWED
   - Auto-approve Check (₹8,500 > ₹5,000 threshold): EXCEEDS AUTO-APPROVE
4. FRAUDGUARD scores transaction:
   - Computed RISK SCORE: 48/100 (MEDIUM RISK due to high single-value amount)
5. System renders decision: REVIEW (Pending Human Approval).
6. System dispatches real-time alert (Push Notification / Webhook / Dashboard Alert).
7. USER receives notification on mobile app / Approval Center:
   - Displays transaction breakdown, RISK SCORE (48/100), and XAI explanation.
8. USER inspects details and taps "APPROVE TRANSACTION".
9. System updates intent state to AUTHORIZED and executes payment adapter.
10. AI AGENT receives callback: PAYMENT_SUCCESSFUL.
```

---

## Journey 4: Suspicious Transaction & Block

### Actors: AI AGENT, AGENTGUARD, FRAUDGUARD, SECURITY ANALYST

```
1. Compromised or ill-prompted AI AGENT attempts to spend ₹25,000 at "Unverified Digital Casino".
2. AI AGENT submits PAYMENT INTENT payload:
   - Amount: ₹25,000
   - Merchant: "Unverified Digital Casino"
   - Category: "Gambling"
3. AGENTGUARD evaluates:
   - Single Limit Check (₹25,000 > ₹10,000 limit): FAIL
   - Category Check ("Gambling"): FORBIDDEN / BLOCKED CATEGORY
4. FRAUDGUARD scores transaction:
   - Merchant Trust Score: 05/100
   - Velocity Anomaly: High
   - Computed RISK SCORE: 94/100 (CRITICAL RISK)
5. XAI ENGINE generates rationale:
   - "Transaction BLOCKED. Exceeds single limit ₹10,000 by 150%. Category 'Gambling' is explicitly forbidden by user policy. Merchant has low trust rating (05/100)."
6. System renders decision: BLOCK.
7. Payment execution is instantly TERMINATED before contacting gateway rails.
8. Security Alert triggered; AGENT status flagged for inspection; Audit Trail logs complete decision trace.
```

---

## Journey 5: Emergency Stop ("Kill Switch")

### Actor: USER (Human Account Owner)

```
1. USER notices unexpected behavior or suspects prompt injection attack across agents.
2. USER hits "EMERGENCY STOP" button on the AGENTPAY mobile app / web console.
3. System updates all agent statuses for that user to SUSPENDED.
4. Any active or pending PAYMENT INTENT requests are immediately canceled.
5. All future API requests from agents return 403 Forbidden until manually reinstated by USER.
```
