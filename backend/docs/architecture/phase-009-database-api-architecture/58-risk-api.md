# AGENTPAY — 58: FRAUDGUARD ML Risk Evaluation API Specification

## 1. Risk Microservice Endpoint

* `POST /api/v1/risk/assess`: Internal Python FastAPI service evaluating 12-D transaction feature vector using XGBoost anomaly classifier.

Returns `risk_score` (0-100), `risk_level`, `decision`, and SHAP feature attribution weights.
