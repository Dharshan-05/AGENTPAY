# AGENTPAY — 38: OWASP, PCI-DSS & NIST Zero Trust Compliance Mapping

## 1. Compliance Framework Mapping Matrix

| Framework | Control / Standard | AGENTPAY Security Architecture Mapping | Design Status |
| :--- | :--- | :--- | :--- |
| **OWASP Top 10** | A01: Broken Access Control | BOLA / IDOR 5-part ownership check + PostgreSQL RLS | DESIGNED |
| **OWASP Top 10** | A02: Cryptographic Failures | TLS 1.3 + AES-256-GCM + Argon2id password hashing | DESIGNED |
| **OWASP Top 10** | A03: Injection | 100% Parameterized prepared statements (Prisma/Drizzle) | DESIGNED |
| **OWASP API Top 10** | API1: Broken Object Level Auth | Row-Level Security Policies + Tenant Context Injection | DESIGNED |
| **OWASP API Top 10** | API2: Broken Authentication | HMAC-SHA256 Signed headers + Replay Nonce Caching | DESIGNED |
| **OWASP LLM Top 10** | LLM01: Prompt Injection | Prompt Role Isolation + AGENTGUARD External Policy Gates | DESIGNED |
| **OWASP LLM Top 10** | LLM02: Insecure Output Handling | JSON Schema Validation + Tool Capability Scope Limits | DESIGNED |
| **PCI-DSS Principles** | Req 3: Protect Stored Card Data | Zero Card/PIN in LLM Context; Tokenized Razorpay Vault | DESIGNED |
| **PCI-DSS Principles** | Req 10: Log and Monitor Access | Append-Only Cryptographic Block Hash Audit Chains | DESIGNED |
| **NIST SP 800-207** | Zero Trust Architecture | Continuous 9-step server-side validation on every request | DESIGNED |
