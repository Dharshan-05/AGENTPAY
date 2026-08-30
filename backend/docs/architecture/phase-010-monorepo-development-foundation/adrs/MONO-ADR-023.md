# MONO-ADR-023: Git Pre-Commit & Pre-Push Hook Automation

## 1. Context & Problem Statement
Preventing unformatted code, lint errors, type failures, or plaintext secrets from being committed or pushed.

## 2. Decision
Configure `husky` and `lint-staged` pre-commit hooks to execute Prettier formatting, ESLint fixes, and Gitleaks secret detection automatically.

## 3. Consequences & Trade-Offs
* **Benefits**: 100% clean repository history without manual formatting commits.
* **Trade-Offs**: Adds a 2-3 second delay to git commit commands.
