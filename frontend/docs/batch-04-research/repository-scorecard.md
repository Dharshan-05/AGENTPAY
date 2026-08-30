# AGENTPAY BATCH 04 REPOSITORY RESEARCH SCORECARD

| Domain | Primary Repository | Score | Secondary Repository | Score | Tertiary Repository | Score | Primary Architectural Focus |
|---|---|---|---|---|---|---|---|
| **035 Contracts** | Temporal | 97 | Trigger.dev | 95 | n8n | 92 | Smart contract execution state machine, idempotent retries |
| **036 Wallets** | Stripe OpenAPI | 96 | HyperSwitch | 95 | Fineract | 91 | Crypto/Treasury wallet balances, mTLS vault signatures |
| **037 Gateways** | Juspay HyperSwitch | 98 | Stripe OpenAPI | 96 | Adyen Docs | 94 | Dynamic PSP routing, failover rules, connector health |
| **038 Fees** | Stripe OpenAPI | 97 | Kill Bill | 94 | Lago | 92 | Interchange++ fee calculation, platform margin split |
| **039 Taxes** | Stripe OpenAPI | 96 | ERPNext | 93 | Lago | 90 | VAT/GST calculation rules, cross-border tax compliance |
| **040 Audit Logs** | SigNoz | 96 | OpenTelemetry | 95 | Grafana | 94 | Cryptographically chained SHA-256 system audit stream |
| **041 Notifications** | Trigger.dev | 96 | n8n | 94 | PostHog | 91 | Webhook retry cadence, multi-channel alerting engine |
| **042 Compliance** | Keycloak | 96 | Authentik | 94 | Ory Kratos | 92 | AML sanctions screening, KYC risk scoring, PEP checks |
| **043 FX Rates** | Stripe OpenAPI | 97 | HyperSwitch | 95 | Fineract | 92 | Real-time foreign exchange rates, treasury hedging |
| **044 System Health** | Grafana | 97 | SigNoz | 96 | OpenTelemetry | 95 | PSP latency telemetry, endpoint uptime, circuit breakers |
