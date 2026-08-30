# AGENTPAY — 43: AI Decision Auditing & Reproducibility Specs

## 1. Reproducibility Specs

To ensure historical AI decision auditability, every logged authorization record links:
1. Exact `prompt_template_version` hash.
2. `model_version` identifier (`fraudguard_xgb_v1.4.2`).
3. Extracted 12-D feature vector values.
4. Generated SHAP feature weights.
5. Final AGENTGUARD authorization decision payload.
