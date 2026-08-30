# AGENTPAY — 27: SHAP Feature Attribution & Natural Text Explanation Synthesis

## 1. XAI Pipeline Architecture

For every risk evaluation, SHAP calculates exact feature attribution weights. A text synthesizer converts top features into natural language user explanations:

```json
{
  "risk_score": 78,
  "risk_level": "HIGH_RISK",
  "top_features": [
    { "feature": "amount_z_score", "weight": 0.42, "description": "Amount is 4.2x above historical average" },
    { "feature": "velocity_60s", "weight": 0.31, "description": "3 intent requests in past 60s" }
  ],
  "explanation_text": "Transaction flagged for REVIEW. Amount (₹45,000) significantly exceeds normal spending patterns and velocity limits."
}
```
