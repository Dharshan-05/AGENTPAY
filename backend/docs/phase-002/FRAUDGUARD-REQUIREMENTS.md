# AGENTPAY — FraudGuard Requirements

## 1. Overview

**FRAUDGUARD** is the explainable AI fraud detection and transaction risk engine of AGENTPAY. It evaluates real-time transaction intents against behavioral baselines, merchant reputation scores, anomaly heuristics, and ML scoring classifiers to calculate a normalized `RISK SCORE` (0 - 100).

---

## 2. Requirement Baseline

### 2.1 Feature Calculation Requirements
* **REQ-FRD-001**: FRAUDGUARD shall extract and calculate twelve primary risk feature dimensions for every evaluated `PAYMENT INTENT`:
  1. `amount_z_score`: Standard deviations of intent amount relative to agent historical mean.
  2. `velocity_60s`: Number of intent requests initiated by agent in past 60 seconds.
  3. `velocity_15m`: Number of distinct merchants targeted by agent in past 15 minutes.
  4. `merchant_trust_score`: Merchant domain/MID trust score fetched from reputation registry.
  5. `category_risk_weight`: Standard Merchant Category Code (MCC) baseline fraud weight.
  6. `user_baseline_ratio`: Intent amount divided by human user average purchase size.
  7. `agent_age_days`: Time elapsed since agent registration.
  8. `historical_failure_rate`: Ratio of failed/blocked attempts to total historical intents for agent.
  9. `off_hours_flag`: Boolean flag indicating intent creation outside agent normal active hours.
  10. `geo_mismatch_flag`: Discrepancy flag between agent API IP ASN and user registered country.
  11. `context_length_delta`: Anomaly delta in length/structure of context metadata.
  12. `behavioral_anomaly_score`: Statistical distance metric from historical agent behavior vector.

### 2.2 Model Scoring & Risk Level Assignment
* **REQ-FRD-002**: The risk engine shall process the feature vector to generate:
  * `risk_score`: Normalized integer from 0 to 100.
  * `fraud_probability`: Floating point probability value between $0.00$ and $1.00$.
* **REQ-FRD-003**: The system shall map `risk_score` values to standardized risk levels:
  * `00 - 35`: `LOW_RISK`
  * `36 - 69`: `MEDIUM_RISK`
  * `70 - 89`: `HIGH_RISK`
  * `90 - 100`: `CRITICAL_RISK`

### 2.3 Output Data Schema
* **REQ-FRD-004**: FRAUDGUARD shall produce a structured JSON response matching the canonical schema containing `intent_id`, `agent_id`, `risk_score`, `fraud_probability`, `risk_level`, `decision`, `reason_codes`, and `explanation` structure.

### 2.4 Performance & Latency Requirements
* **REQ-FRD-005**: Feature extraction and risk model execution shall complete in $\le 50\text{ ms}$ at $p_{99}$ latency.
* **REQ-FRD-006**: Feature lookups for historical baselines and velocity counters shall be cached in Redis to satisfy latency bounds.

### 2.5 Cold-Start & Model Degradation Fallbacks
* **REQ-FRD-007**: For newly registered agents with no historical transaction baseline (cold-start), FRAUDGUARD shall apply conservative default baseline weights and default to owner policy constraints.
* **REQ-FRD-008**: If the ML scoring classifier is unavailable or times out (> 100ms), FRAUDGUARD shall fall back to deterministic statistical rule evaluation and assign a minimum `MEDIUM_RISK` level to ensure fail-safe security.
