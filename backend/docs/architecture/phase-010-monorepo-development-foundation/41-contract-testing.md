# AGENTPAY — 41: OpenAPI & Zod Contract Testing Automation

## 1. Contract Test Specification

* Compares API response payloads returned by `apps/api` controllers directly against OpenAPI 3.0 schema definitions using `jest-openapi` / `vitest-openapi`.
* CI build fails if controller output violates the published OpenAPI spec contract.
