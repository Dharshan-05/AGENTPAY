# AGENTPAY BATCH 07 REPOSITORY RESEARCH SCORECARD

| Domain | Primary Repository | Score | Secondary Repository | Score | Tertiary Repository | Score | Primary Architectural Focus |
|---|---|---|---|---|---|---|---|
| **065 Products Catalog** | Medusa | 98 | Saleor | 96 | Vendure | 93 | Advanced catalog variants, multi-option matrices |
| **066 Order Management** | Medusa | 98 | Stripe OpenAPI | 97 | Saleor | 95 | Order fulfillment matrix, multi-state transitions |
| **067 Order Item Breakdown** | Medusa | 97 | ERPNext | 95 | Vendure | 92 | Granular item line allocations & SKU tax splits |
| **068 Inventory Control** | ERPNext | 98 | Medusa | 96 | Odoo | 94 | Multi-warehouse stock movement & safety levels |
| **069 Stock Reservations** | Medusa | 97 | Saleor | 95 | Vendure | 93 | TTL-backed allocation engine & auto-release |
| **070 Shipment Dispatch** | Medusa | 97 | Saleor | 95 | ERPNext | 93 | Multi-carrier logistics dispatch & parcel tracking |
| **071 Rate Matrices** | Medusa | 96 | Stripe OpenAPI | 95 | Vendure | 92 | Carrier rate priority rules & fuel surcharge matrices |
| **072 Address Verification** | Stripe OpenAPI | 98 | Medusa | 96 | Keycloak | 93 | CASS/Loqate geo-validation & tax nexus signals |
| **073 Session Control** | Stripe OpenAPI | 99 | Juspay HyperSwitch | 97 | Medusa | 95 | Checkout session security, TTL expiry & revocation |
| **074 Payment Attempt Logs** | Juspay HyperSwitch | 99 | Stripe OpenAPI | 98 | Adyen Docs | 96 | Attempt retry matrix, 3DS & PSP response codes |
