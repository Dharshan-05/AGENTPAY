# AGENTPAY BATCH 03 REPOSITORY RESEARCH SCORECARD

| Domain | Primary Repository | Score | Secondary Repository | Score | Tertiary Repository | Score | Primary Architectural Focus |
|---|---|---|---|---|---|---|---|
| **025 Subscriptions** | Stripe OpenAPI | 97 | Kill Bill | 95 | Lago | 92 | Subscription lifecycle states, trial periods, dunning retries |
| **026 Invoices** | Stripe OpenAPI | 97 | ERPNext | 94 | Saleor | 88 | Itemized billing lines, tax calculations, credit notes |
| **027 Billing** | Lago | 96 | Kill Bill | 94 | Stripe OpenAPI | 93 | Metered usage aggregation, billing cycles, balance tracking |
| **028 Plans** | Lago | 96 | Stripe OpenAPI | 95 | Kill Bill | 91 | Tiered pricing models, entitlement limits, plan versioning |
| **029 Customer Segments** | Segment | 95 | PostHog | 93 | RudderStack | 90 | Behavioral cohorts, risk score tiers, dynamic user traits |
| **030 Transaction Search** | Stripe OpenAPI | 97 | Juspay HyperSwitch | 96 | ERPNext | 89 | Multi-axis filter criteria, cross-connector investigation |
| **031 Payment Links** | Stripe OpenAPI | 97 | Medusa | 89 | Saleor | 86 | Ephemeral payment URLs, usage limits, QR payloads |
| **032 Checkout** | Stripe OpenAPI | 97 | Juspay HyperSwitch | 96 | Medusa | 90 | 3DS challenge orchestration, payment session recovery |
| **033 Mandates** | Stripe OpenAPI | 97 | Juspay HyperSwitch | 96 | Apache Fineract | 91 | UPI e-Mandate, ACH direct debit authorization rules |
| **034 Recurring Payments** | Stripe OpenAPI | 97 | Kill Bill | 95 | Lago | 92 | Automated dunning cadence, smart retry routing |
