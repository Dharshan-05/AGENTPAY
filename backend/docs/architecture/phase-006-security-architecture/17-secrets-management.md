# AGENTPAY — 17: Production Secrets Management & Zero-Git Policy

## 1. Secrets Management Rules

1. **Zero Secrets in Git**: Plaintext API keys, database passwords, JWT secrets, or Razorpay credentials in source code or Git repositories are strictly prohibited.
2. **Environment Variable Injection**: Local development uses `.env.local` files added to `.gitignore`.
3. **Production Secret Manager**: Production secrets are stored in HashiCorp Vault or AWS Secrets Manager and injected dynamically into container environment variables at pod startup.
4. **Secret Scanning**: GitHub Actions workflow runs automated secret scanning on every commit.
