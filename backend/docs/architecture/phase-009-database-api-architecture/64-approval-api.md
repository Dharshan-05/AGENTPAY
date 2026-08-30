# AGENTPAY — 64: Approval Center Escalation REST API Specification

## 1. Approval Center Endpoints

* `GET /api/v1/approvals`: List pending human escalation cards (`status = PENDING`).
* `GET /api/v1/approvals/{approval_id}`: Fetch specific escalation card payload & XAI trace.
* `POST /api/v1/approvals/{approval_id}/action`: Action approval card (`action: "APPROVE" | "REJECT"`).
