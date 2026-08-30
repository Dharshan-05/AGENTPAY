# AGENTPAY BATCH 05 REPOSITORY RESEARCH SCORECARD

| Domain | Primary Repository | Score | Secondary Repository | Score | Tertiary Repository | Score | Primary Architectural Focus |
|---|---|---|---|---|---|---|---|
| **045 Products** | Medusa | 97 | Saleor | 95 | Vendure | 92 | Catalog SKU variants, multi-currency price lists |
| **046 Orders** | Medusa | 97 | Stripe OpenAPI | 96 | Saleor | 94 | Order state machine, payment & fulfillment status |
| **047 Order Items** | Medusa | 96 | ERPNext | 94 | Vendure | 91 | Itemized order lines, tax & discount allocation |
| **048 Inventory** | ERPNext | 97 | Medusa | 95 | Odoo | 93 | Multi-warehouse stock tracking, reorder thresholds |
| **049 Reservations** | Medusa | 96 | Saleor | 94 | Vendure | 92 | TTL-backed stock reservations, release reason trace |
| **050 Shipping** | Medusa | 96 | Saleor | 94 | ERPNext | 92 | Carrier integration, parcel tracking telemetry |
| **051 Shipping Rates** | Medusa | 95 | Stripe OpenAPI | 94 | Vendure | 91 | Dynamic rate matrices, carrier option comparison |
| **052 Addresses** | Stripe OpenAPI | 97 | Medusa | 95 | Keycloak | 92 | Verified geo-addresses, risk & location profiling |
| **053 Sessions** | Stripe OpenAPI | 98 | Juspay HyperSwitch | 96 | Medusa | 94 | Checkout session lifecycle, TTL expiry & recovery |
| **054 Payment Attempts** | Juspay HyperSwitch | 98 | Stripe OpenAPI | 97 | Adyen Docs | 95 | Multi-connector retry attempts, 3DS & auth logs |
