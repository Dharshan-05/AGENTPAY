# AGENTPAY — 46: 5-Tier Data Classification & Sensitivity Handling Rules

## 1. 5-Tier Data Classification Matrix

| Classification Tier | Target Data | Security & Encryption Requirement |
| :--- | :--- | :--- |
| **Tier 1: PUBLIC** | Public merchant names, product catalogs | Plaintext read access |
| **Tier 2: INTERNAL** | Agent names, non-sensitive audit metadata | RLS tenant isolation |
| **Tier 3: CONFIDENTIAL** | User email, order items, transaction history| RLS + TLS 1.3 in transit |
| **Tier 4: SENSITIVE PII** | Phone numbers, user addresses | Application-level AES-256 GCM encryption |
| **Tier 5: RESTRICTED** | HMAC signing keys, webhook secrets | HashiCorp Vault injection (Never DB) |
