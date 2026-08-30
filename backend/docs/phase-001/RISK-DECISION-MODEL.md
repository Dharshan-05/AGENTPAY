# AGENTPAY — Risk Decision Model (FRAUDGUARD)

## 1. Risk Dimension Matrix

**FRAUDGUARD** computes transaction risk by evaluating twelve primary feature dimensions across historical baselines, contextual signals, and real-time behavioral telemetry:

```
+-----------------------------------------------------------------------------------+
|                            FRAUDGUARD RISK DIMENSIONS                             |
+-------------------+-------------------+-------------------+-----------------------+
| 1. Amount Anomaly | 2. Velocity/Freq  | 3. Merchant Risk  | 4. User Baseline      |
| 5. Agent Baseline | 6. Patterns       | 7. Spending Spike | 8. Location/IP Context|
| 9. Device/Session | 10. Time Window   | 11. Category Risk | 12. Behavioral Delta  |
+-------------------+-------------------+-------------------+-----------------------+
```

### Risk Dimension Details

| Dimension | Description | Signal Calculation |
| :--- | :--- | :--- |
| **Transaction Amount** | Deviation of current intent amount relative to historical agent mean. | Z-score of transaction amount against 30-day agent mean. |
| **Transaction Frequency** | Spike in request rate over short sliding time windows. | Number of intents created in past 60s / 5m window. |
| **Merchant Risk Score** | Reputation and historical fraud rate of target domain/MID. | Merchant trust database score (0 - 100). |
| **User Spending Baseline** | Alignment with human account owner historical spending scale. | Ratio of intent amount to user's average spending. |
| **Agent Behavior Delta** | Change in product/service requesting patterns. | Vector distance in embedding space vs historical intent prompts. |
| **Velocity Anomalies** | Rapid successive payments across multiple merchants. | Distinct merchants targeted within 15-minute window. |
| **Location & IP Context** | Geographic origin of agent API request vs user registration. | Country / ASN discrepancy flag. |
| **Transaction Timing** | Intent initiation during unusual off-hours. | Hour-of-day probability distribution match. |
| **Category Risk Weight** | Baseline fraud prevalence in target Merchant Category Code (MCC). | Standard MCC risk weighting table. |

---

## 2. Risk Output Schema

For every evaluated transaction, FRAUDGUARD produces a standardized structured output payload:

```json
{
  "intent_id": "intent_7f8a9b0c",
  "agent_id": "agt_98a12c44",
  "risk_score": 78,
  "fraud_probability": 0.82,
  "risk_level": "HIGH_RISK",
  "decision": "BLOCK",
  "reason_codes": [
    "ERR_AMOUNT_EXCEEDS_BASELINE",
    "ERR_MERCHANT_LOW_REPUTATION",
    "ERR_OFF_HOURS_VELOCITY"
  ],
  "explanation": {
    "summary": "Transaction BLOCKED. Amount (₹25,000) is 4.2x above historical agent mean. Merchant 'Unverified Digital Casino' has a low trust score (05/100).",
    "top_features": [
      { "feature": "category_restriction", "weight": -0.45, "impact": "High Negative" },
      { "feature": "amount_z_score", "weight": 3.8, "impact": "High Risk Spike" },
      { "feature": "merchant_reputation", "weight": 0.05, "impact": "High Risk Spike" }
    ]
  }
}
```

---

## 3. Decision Framework & Configurable Thresholds

The canonical decision framework maps composite `RISK SCORE` (0 - 100) and AGENTGUARD policy checks to action outcomes:

```
                  +-------------------------+
                  |  COMPUTED RISK SCORE    |
                  +-------------------------+
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
[ 00 - 35 ]             [ 36 - 69 ]             [ 70 - 89 ]             [ 90 - 100 ]
  LOW RISK                MEDIUM RISK              HIGH RISK               CRITICAL RISK
     │                       │                       │                       │
     ▼                       ▼                       ▼                       ▼
  ALLOW                   REVIEW                  BLOCK                   BLOCK
 (Auto-Approve          (Escalate to            (Terminate              (Terminate +
  if policy              Approval                Payment                 Alert + Suspend
  permits)               Center)                 Intent)                 Agent Identity)
```

### Configurable Threshold Rules

* Financial thresholds and risk boundaries are **NEVER hard-coded**. They are loaded dynamically from user policy profiles and system configuration files.
* Users can adjust their personal risk tolerance (e.g., conservative users require human review for scores > 30, while aggressive users permit auto-approval up to score 50).
