# AGENTPAY — 66: Reconciliation Management & Discrepancy API Specs

## 1. Reconciliation REST Endpoints

* `GET /api/v1/reconciliation/batches`: List historical reconciliation job batches.
* `GET /api/v1/reconciliation/discrepancies`: List active settlement discrepancies.
* `POST /api/v1/reconciliation/discrepancies/{id}/resolve`: Manually resolve settlement discrepancy with audit reason.
