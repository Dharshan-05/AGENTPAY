# AGENTPAY — 28: Secret Storage Policy (HashiCorp Vault / Zero DB Secrets)

## 1. Zero Plaintext Database Secrets Policy

1. **No Gateway API Keys**: Razorpay secret API keys, webhook signing secrets, and OAuth client secrets are strictly banned from PostgreSQL table storage.
2. **HashiCorp Vault Integration**: Secrets are injected into runtime environment variables using HashiCorp Vault or AWS Secrets Manager.
3. **Encrypted Credentials**: Public cryptographic verification keys are stored using `BYTEA` or base64 text columns.
