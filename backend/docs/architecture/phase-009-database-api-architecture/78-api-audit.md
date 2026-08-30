# AGENTPAY — 78: Automated API Mutation Security Audit Logging

## 1. Audit Middleware Engine

Every state-mutating API HTTP call (`POST`, `PUT`, `DELETE`) automatically triggers audit event creation via interceptor middleware, recording `actor_id`, `resource_id`, `old_state`, `new_state`, and SHA-256 block hashes into `audit_events`.
