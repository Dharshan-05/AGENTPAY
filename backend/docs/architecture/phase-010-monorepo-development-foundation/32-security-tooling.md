# AGENTPAY — 32: Security Tooling Integration (Gitleaks, Semgrep, OSV Audit)

## 1. Security CLI Commands

* `pnpm security:scan`: Runs `gitleaks detect` and `semgrep --config p/security-audit`.
* `pnpm security:audit`: Runs `pnpm audit --prod` checking for vulnerable npm dependencies.
