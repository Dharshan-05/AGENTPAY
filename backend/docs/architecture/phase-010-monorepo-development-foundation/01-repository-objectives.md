# AGENTPAY — 01: Monorepo Foundation Core Architectural Objectives

## 1. Core Objectives

The primary goal of Phase 010 is to create an authoritative, production-grade PNPM workspace monorepo foundation that houses AGENTPAY, AGENTGUARD, and FRAUDGUARD.

---

## 2. Key Pillars

1. **Reproducibility**: Environment configuration and toolchains are strictly pinned (`Node v20.x`, `PNPM v9.x`, `Python 3.11`).
2. **Type-Safety**: End-to-end type safety across shared packages (`@agentpay/types`, `@agentpay/api-contracts`) preventing contract drift.
3. **Security by Default**: Zero plaintext secrets committed to git, mandatory environment variable validation via Zod at startup.
4. **Developer Experience**: Single command (`pnpm dev`) boots local infrastructure (PostgreSQL, Redis) and application services.
