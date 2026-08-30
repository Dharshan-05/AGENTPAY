# AGENTPAY Database Seed Data Architecture (Phase 078)

## Executive Summary

This document formalizes the production-safe, environment-aware database seeding architecture for **AGENTPAY** (`Phase 078`).

The seed engine ([seeder.py](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/seeder.py)) provides deterministic, synthetic seed data for local development, testing, and demo environments while strictly prohibiting execution against production databases.

---

## 1. Safety Rules & Enforcements

1. **Strict Production Environment Rejection**: Seeding attempts where `AGENTPAY_ENV` is set to `production`, `prod`, or `live` automatically raise `ProductionSeedingProhibitedError` and abort immediately.
2. **Zero Real Secrets**: All passwords use synthetic, non-real password hashes; zero raw API keys, card PAN, CVV, PIN, or tokens are populated.
3. **Idempotency**: Running `seed_all()` multiple times is idempotent. Records are checked by tenant-scoped references/IDs before creation, avoiding duplicate errors or data bloat.
4. **Foreign Key Order Integrity**: Entities are seeded in strict dependency order:
   `Users -> Merchants -> Agents -> Categories -> Products -> Offers -> Inventory -> Policies -> Rules -> Payment Orders -> Payment Transactions -> Audit Logs -> Security Events -> Attack Simulations -> Risk Decision Audits`.

---

## 2. Seeded Entities & Deterministic Identifiers

| Entity | Reference / Key | Seed Namespace UUID | Environment Scope |
| :--- | :--- | :--- | :--- |
| Tenant | Baseline Multi-tenant | `00000000-0000-4000-a000-000000000001` | Dev / Test / Demo |
| User | `seed.reviewer@agentpay.internal` | `00000000-0000-4000-a000-000000000002` | Dev / Test / Demo |
| Merchant | `MERCH-SEED-001` | `00000000-0000-4000-a000-000000000003` | Dev / Test / Demo |
| Agent | `AGENT-SEED-001` | `00000000-0000-4000-a000-000000000004` | Dev / Test / Demo |
| Product Category | `CAT-SEED-001` | `00000000-0000-4000-a000-000000000006` | Dev / Test / Demo |
| Product | `PROD-SEED-001` | `00000000-0000-4000-a000-000000000005` | Dev / Test / Demo |
| Offer | `OFFER-SEED-001` | `00000000-0000-4000-a000-000000000007` | Dev / Test / Demo |
| Security Policy | `POL-SEED-001` | `00000000-0000-4000-a000-000000000008` | Dev / Test / Demo |
| Policy Rule | `RULE-SEED-001` | `00000000-0000-4000-a000-000000000009` | Dev / Test / Demo |
| Payment Order | `ORD-SEED-001` | `00000000-0000-4000-a000-000000000010` | Dev / Test / Demo |
| Payment Transaction | `TXN-SEED-001` | `00000000-0000-4000-a000-000000000011` | Dev / Test / Demo |
| Audit Log | `AUD-SEED-001` | Dynamic UUIDv7 | Dev / Test / Demo |
| Security Event | `SE-SEED-001` | Dynamic UUIDv7 | Dev / Test / Demo |
| Attack Simulation | `SIM-SEED-001` | Dynamic UUIDv7 | Dev / Test / Demo |
| Risk Decision Audit | `RDA-SEED-001` | Dynamic UUIDv7 | Dev / Test / Demo |
