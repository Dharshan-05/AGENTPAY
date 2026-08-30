# AGENTPAY — 12: Multi-Environment Tier Management (`.env.example` to `Production`)

## 1. Environment Hierarchies

* `.env.example`: Root template containing dummy development keys. Committed to Git.
* `.env.local`: Local developer overrides. **Ignored in `.gitignore`**.
* `.env.test`: Integration test settings pointing to local containerized databases.
* `Production`: Secrets injected via HashiCorp Vault / Cloud Secret Manager at runtime.
