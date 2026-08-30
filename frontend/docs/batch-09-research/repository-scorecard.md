# AGENTPAY BATCH 09 REPOSITORY RESEARCH SCORECARD

| Domain | Primary Repository | Score | Secondary Repository | Score | Tertiary Repository | Score | Primary Architectural Focus |
|---|---|---|---|---|---|---|---|
| **085 API Keys** | Stripe OpenAPI | 99 | Keycloak | 96 | n8n | 94 | Granular API key scoping, IP whitelisting & instant revocation |
| **086 Webhooks Delivery** | Juspay HyperSwitch | 98 | Stripe OpenAPI | 97 | n8n | 95 | Webhook event dispatch, exponential backoff retries & HMAC signatures |
| **087 Tokenization Vault** | Juspay HyperSwitch | 99 | Stripe OpenAPI | 97 | Keycloak | 94 | PCI SAQ-A tokenization vault, surrogate tokens & Key Encryption Keys |
| **088 3DS Authentication** | Stripe OpenAPI | 98 | Juspay HyperSwitch | 97 | Adyen Specs | 95 | 3D Secure 2.0 challenge/frictionless authentication flow |
| **089 Discrepancy Resolution** | Apache Fineract | 98 | ERPNext | 95 | Kill Bill | 93 | Ledger exception resolution & automated write-off auditing |
| **090 Partner Integrations** | Juspay HyperSwitch | 99 | Stripe OpenAPI | 96 | Medusa | 94 | PSP connector health, sandbox testing & API credential vaults |
| **091 Tenant Isolation** | Keycloak | 98 | Frappe Framework | 95 | Odoo | 93 | Virtual tenant boundaries, row-level isolation & multi-org RBAC |
| **092 KYC Verification** | Stripe OpenAPI | 98 | Keycloak | 95 | ERPNext | 93 | Identity verification, document OCR verification & PEP checks |
| **093 Sanctions Screening** | Apache Fineract | 98 | Keycloak | 96 | ERPNext | 94 | OFAC / UN sanctions list screening & fuzzy matching rules |
| **094 Disaster Recovery** | n8n | 98 | Juspay HyperSwitch | 96 | Keycloak | 93 | Multi-region failover matrix, RPO/RTO telemetry & HA health |
