# AGENTPAY — 72: Safe Whitelisted Query Parameter Filtering Specification

## 1. Query Filtering Rules

* **Explicit Whitelist**: Filters allowed exclusively on pre-indexed columns (`status`, `merchant_id`, `agent_id`, `created_after`, `created_before`).
* **SQL Injection Prevention**: Filter parameters are passed as parameterized SQL arguments; raw query string concatenation is banned.
