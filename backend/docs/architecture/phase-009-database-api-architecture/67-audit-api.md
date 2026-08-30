# AGENTPAY — 67: Read-Only Audit Log Search REST API Contracts

## 1. Audit API Endpoints

* `GET /api/v1/audit/events`: Search immutable security audit logs filtered by `actor_id`, `resource_type`, `action`, or date range.
* `GET /api/v1/audit/events/{audit_id}/verify`: Verify SHA-256 block chain hash integrity for a target audit record.
