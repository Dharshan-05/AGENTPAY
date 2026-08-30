# AGENTPAY — Payment Lifecycle & Pipeline

## 1. Canonical Payment Trust Pipeline

Every financial transaction initiated by an AI AGENT follows a strict 15-step execution pipeline within AGENTPAY. No transaction can bypass any stage of this pipeline.

```
 [1. Intent Creation]
          │
          ▼
 [2. Authenticate Agent] ──(Fail)──> REJECT (401)
          │
          ▼
 [3. Verify Permissions] ──(Fail)──> REJECT (403)
          │
          ▼
 [4. User Auth Check] ────(Fail)──> REJECT (403)
          │
          ▼
 [5. Validate Params] ────(Fail)──> REJECT (400)
          │
          ▼
 [6. AGENTGUARD Policy Engine] ──(Policy Violation)──> BLOCK
          │
          ▼
 [7. FRAUDGUARD Feature Extraction]
          │
          ▼
 [8. Calculate RISK SCORE]
          │
          ▼
 [9. XAI Explanation Generation]
          │
          ▼
 [10. Determine Authorization Level]
          │
          ├── Low Risk / Within Auto-Limit ──> [12. Execute Payment]
          ├── Medium Risk / Exceeds Limit ───> [11. Human Approval] ──(Rejected)──> REJECT
          │                                           │ (Approved)
          │                                           ▼
          │                                  [12. Execute Payment]
          └── High/Critical Risk ─────────────> BLOCK
                                                      │
                                                      ▼
                                             [13. Verify Payment Result]
                                                      │
                                                      ▼
                                             [14. Monitor Transaction]
                                                      │
                                                      ▼
                                             [15. Immutable Audit Trail]
```

---

## 2. Pipeline Step Specifications

1. **Intent Creation**: AI AGENT submits payload detailing merchant, amount, category, currency, and idempotency key.
2. **Authenticate Agent**: Verify HMAC cryptographic signature and API key against active registry.
3. **Verify Agent Permissions**: Ensure agent status is `ACTIVE` and scope grants transaction creation privileges.
4. **Validate User Authorization**: Verify owner account status is active and emergency stop is NOT engaged.
5. **Validate Transaction Parameters**: Schema validation (non-zero positive amount, recognized currency, valid merchant data).
6. **Run AGENTGUARD Policies**: Evaluate static rules (limits, category white/blacklists, operating hours, velocity).
7. **Run FRAUDGUARD Risk Analysis**: Extract feature vector (behavioral delta, merchant trust score, context anomalies).
8. **Calculate Transaction Risk**: Model computes normalized `RISK SCORE` (0 - 100) and `FRAUD PROBABILITY`.
9. **Generate Explanation**: XAI engine produces top feature attributions and natural language rationale.
10. **Determine Authorization Level**: System maps policy + risk score to decision (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`).
11. **Request Human Approval**: If decision is `REVIEW`, dispatch real-time alert and pause intent awaiting human confirmation.
12. **Execute Payment**: Forward authorized payment intent payload to underlying gateway adapter (e.g. Razorpay / UPI).
13. **Verify Payment Result**: Process settlement response from processor, verifying payment status.
14. **Monitor Transaction**: Post-execution velocity checks and fraud pattern updates.
15. **Record Immutable Audit Trail**: Write end-to-end trace (intent, policy results, risk scores, XAI output, execution response) to immutable log store.

---

## 3. Payment Intent State Machine

```
               +-------------------+
               |      CREATED      |
               +-------------------+
                         │
                         ▼
               +-------------------+
               |     POLICIED      |
               +-------------------+
                         │
                         ▼
               +-------------------+
               |      SCORED       |
               +-------------------+
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
+---------------+ +--------------+ +---------------+
|   AUTHORIZED  | |PENDING_APP...| |   REJECTED    | (Terminal: Blocked by Policy/Fraud/User)
+---------------+ +--------------+ +---------------+
        │                │
        │                ▼ (Human Approved)
        │         +--------------+
        └────────>|  PROCESSING  |
                  +--------------+
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
+---------------+                 +---------------+
|   EXECUTED    |                 |    FAILED     | (Terminal: Payment gateway error)
+---------------+                 +---------------+
(Terminal Success)
```

---

## 4. Idempotency & Double-Spend Safeguards

To prevent an autonomous AI AGENT from executing duplicate transactions due to network retries or logic loops:

* Every `PAYMENT INTENT` requires a unique `idempotency_key` (UUID v4) provided in the request payload.
* The API edge caches `idempotency_key` entries in Redis for 24 hours.
* If a duplicate `idempotency_key` is received within the retention window, AGENTPAY returns the cached processing response without re-triggering policy, fraud scoring, or payment execution.
