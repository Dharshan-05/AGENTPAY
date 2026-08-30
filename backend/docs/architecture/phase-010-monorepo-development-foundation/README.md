# AGENTPAY — Phase 010: Monorepo & Development Foundation Architecture

## Executive Summary

Phase 010 establishes the authoritative, production-ready, reproducible monorepo development foundation for **AGENTPAY** (Autonomous Payment Infrastructure), **AGENTGUARD** (AI-Agent Policy, Security & Authorization Layer), and **FRAUDGUARD** (Explainable AI Fraud & Risk Engine).

This phase translates the approved system architecture (Phase 005), security architecture (Phase 006), AI/agent architecture (Phase 007), payment architecture (Phase 008), and database/API architecture (Phase 009) into a clean, testable, type-safe, and developer-friendly repository baseline.

---

## Workspace Architecture Overview

```
D:\PROJECT\ANGENT PAY
├── apps/
│   ├── web/               # Next.js / React TypeScript User & Merchant Dashboard
│   ├── api/               # Express / Node.js TypeScript REST Core Payment Gateway
│   ├── agent-runtime/     # Python FastAPI / LangChain Autonomous Agent Execution Engine
│   ├── agentguard/        # Express / Node.js Policy & Security Control Plane
│   └── worker/            # Node.js Background Task & Transactional Outbox Worker
├── packages/
│   ├── config/            # Typed Zod environment and app configuration
│   ├── types/             # Shared TypeScript domain models & primitive interfaces
│   ├── api-contracts/     # Zod request/response validation schemas & OpenAPI specs
│   ├── database/          # PostgreSQL client, Prisma/Kysely migrations, repositories
│   ├── auth/              # JWT, OAuth2, mTLS, HMAC authentication primitives
│   ├── security/          # Encryption, hashing, WAF headers & secret utilities
│   ├── payments/          # Razorpay adapter, state machine & settlement engine
│   ├── agent-core/        # Autonomous agent capability & tool execution models
│   ├── agentguard-core/   # Security policy rules, trust evaluation & kill-switch logic
│   ├── events/            # Standardized domain event schemas & outbox publishers
│   ├── observability/     # OpenTelemetry tracing, Prometheus metrics & Winston logger
│   └── test-utils/        # Shared Vitest, Supertest & containerized test fixtures
├── infrastructure/
│   ├── docker/            # Dockerfiles for all microservices & background workers
│   ├── postgres/          # Init scripts & RLS policy definitions
│   └── redis/             # Redis configuration for rate limiting & idempotency
├── .github/
│   └── workflows/         # Production CI/CD pipelines (Lint, Typecheck, Test, Build)
├── pnpm-workspace.yaml    # PNPM workspace definition
├── package.json           # Monorepo root configuration & orchestrator scripts
├── tsconfig.base.json     # Strict master TypeScript compiler configuration
├── docker-compose.yml     # Local developer multi-container orchestration
└── README.md
```

---

## 60 Architecture Specifications Index

1. [01-repository-objectives.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/01-repository-objectives.md)
2. [02-monorepo-strategy.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/02-monorepo-strategy.md)
3. [03-repository-structure.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/03-repository-structure.md)
4. [04-application-boundaries.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/04-application-boundaries.md)
5. [05-package-boundaries.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/05-package-boundaries.md)
6. [06-dependency-graph.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/06-dependency-graph.md)
7. [07-layered-architecture.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/07-layered-architecture.md)
8. [08-typescript-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/08-typescript-foundation.md)
9. [09-node-toolchain.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/09-node-toolchain.md)
10. [10-python-ai-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/10-python-ai-foundation.md)
11. [11-configuration.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/11-configuration.md)
12. [12-environment-management.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/12-environment-management.md)
13. [13-secret-management.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/13-secret-management.md)
14. [14-database-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/14-database-development.md)
15. [15-migration-tooling.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/15-migration-tooling.md)
16. [16-seeding.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/16-seeding.md)
17. [17-postgresql-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/17-postgresql-development.md)
18. [18-redis-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/18-redis-development.md)
19. [19-event-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/19-event-development.md)
20. [20-worker-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/20-worker-foundation.md)
21. [21-api-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/21-api-foundation.md)
22. [22-api-contracts.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/22-api-contracts.md)
23. [23-openapi-tooling.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/23-openapi-tooling.md)
24. [24-frontend-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/24-frontend-foundation.md)
25. [25-api-client.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/25-api-client.md)
26. [26-agent-runtime-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/26-agent-runtime-foundation.md)
27. [27-agentguard-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/27-agentguard-foundation.md)
28. [28-payment-sandbox.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/28-payment-sandbox.md)
29. [29-webhook-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/29-webhook-development.md)
30. [30-authentication-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/30-authentication-foundation.md)
31. [31-authorization-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/31-authorization-foundation.md)
32. [32-security-tooling.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/32-security-tooling.md)
33. [33-git-hooks.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/33-git-hooks.md)
34. [34-commit-conventions.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/34-commit-conventions.md)
35. [35-code-ownership.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/35-code-ownership.md)
36. [36-eslint.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/36-eslint.md)
37. [37-prettier.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/37-prettier.md)
38. [38-testing-strategy.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/38-testing-strategy.md)
39. [39-unit-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/39-unit-testing.md)
40. [40-integration-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/40-integration-testing.md)
41. [41-contract-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/41-contract-testing.md)
42. [42-e2e-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/42-e2e-testing.md)
43. [43-agent-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/43-agent-testing.md)
44. [44-payment-testing.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/44-payment-testing.md)
45. [45-ci-foundation.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/45-ci-foundation.md)
46. [46-build-system.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/46-build-system.md)
47. [47-development-commands.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/47-development-commands.md)
48. [48-docker-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/48-docker-development.md)
49. [49-docker-security.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/49-docker-security.md)
50. [50-observability-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/50-observability-development.md)
51. [51-structured-logging.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/51-structured-logging.md)
52. [52-architecture-enforcement.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/52-architecture-enforcement.md)
53. [53-dependency-governance.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/53-dependency-governance.md)
54. [54-shared-types.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/54-shared-types.md)
55. [55-event-contracts.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/55-event-contracts.md)
56. [56-developer-onboarding.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/56-developer-onboarding.md)
57. [57-windows-development.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/57-windows-development.md)
58. [58-troubleshooting.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/58-troubleshooting.md)
59. [59-mvp-vs-future.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/59-mvp-vs-future.md)
60. [60-final-quality-gate.md](file:///d:/PROJECT/ANGENT%20PAY/docs/architecture/phase-010-monorepo-development-foundation/60-final-quality-gate.md)
