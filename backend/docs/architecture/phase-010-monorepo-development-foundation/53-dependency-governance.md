# AGENTPAY — 53: Package Dependency Review & License Compliance Rules

## 1. Governance Rules

* **Allowed Licenses**: MIT, Apache-2.0, BSD-3-Clause, ISC.
* **Prohibited Licenses**: GPL-3.0, AGPL-3.0 (Virally restrictive licenses).
* **Package Audits**: `pnpm audit` runs weekly in CI to flag zero-day security vulnerabilities in third-party dependencies.
