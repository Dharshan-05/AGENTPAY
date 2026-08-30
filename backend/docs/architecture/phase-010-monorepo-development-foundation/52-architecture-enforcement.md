# AGENTPAY — 52: Dependency Linter & Architectural Boundary Enforcement

## 1. Automated Boundary Checks

* **Rule A**: Direct SQL queries or database pool imports in `apps/api` controllers trigger ESLint failures. Queries must go through `@agentpay/database` repositories.
* **Rule B**: Direct Razorpay SDK imports in `apps/web` or `apps/agent-runtime` trigger lint errors.
* **Rule C**: LLM output parsing bypassing `@agentpay/agentguard-core` triggers build failures.
