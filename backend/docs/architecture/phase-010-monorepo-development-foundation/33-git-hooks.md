# AGENTPAY — 33: Git Pre-Commit & Pre-Push Hooks Setup (`husky` / `lint-staged`)

## 1. Git Hook Automation

* **Pre-commit**: Runs `lint-staged` (Prettier formatting, ESLint fixes, Gitleaks secret detection).
* **Pre-push**: Runs `pnpm typecheck` across all workspace packages.
