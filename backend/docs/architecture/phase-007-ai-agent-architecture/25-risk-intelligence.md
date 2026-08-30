# AGENTPAY — 25: 12-D Feature Extraction & XGBoost Anomaly Scoring

## 1. 12-D Risk Feature Vector

FRAUDGUARD extracts 12 real-time feature dimensions for XGBoost classification:
`amount_z_score`, `velocity_60s`, `velocity_15m`, `merchant_trust_score`, `category_risk_weight`, `user_baseline_ratio`, `agent_age_days`, `historical_failure_rate`, `off_hours_flag`, `geo_mismatch_flag`, `context_length_delta`, `behavioral_anomaly_score`.

Inference produces a normalized `RISK SCORE` (0-100) in $< 30\text{ ms}$.
