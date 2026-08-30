# AGENTPAY — 13: Local & Production Secret Protection Policy

## 1. Secret Protection Rules

1. **Zero Secret Commits**: Plaintext API keys, DB passwords, and private keys are strictly banned from source code.
2. **Automated Secret Scanning**: Pre-commit hooks (`gitleaks`) and CI pipelines scan every pull request for secret patterns.
3. **Sandbox Credentials**: Development environment strictly uses Razorpay Test Mode keys (`rzp_test_*`).
