# AGENTPAY — 03: Complete Directory Layout & Organization

## 1. Directory Blueprint

```
D:\PROJECT\ANGENT PAY
├── apps/                 # Runnable applications
│   ├── web/              # User/Merchant Portal
│   ├── api/              # Core Gateway Backend
│   ├── agent-runtime/    # AI Agent Execution Microservice
│   ├── agentguard/       # Policy & Security Service
│   └── worker/           # Background Outbox Worker
├── packages/             # Internal shared npm modules
│   ├── config/           # Environment validation
│   ├── types/            # TypeScript interfaces
│   ├── api-contracts/    # Zod schemas & OpenAPI
│   ├── database/         # PostgreSQL client & migrations
│   ├── auth/             # Authentication & JWT
│   ├── security/         # Cryptography & HMAC
│   ├── payments/         # Razorpay settlement logic
│   ├── agent-core/       # Agent tool definitions
│   ├── agentguard-core/  # Policy engine rules
│   ├── events/           # Outbox event schemas
│   ├── observability/    # OpenTelemetry & logger
│   └── test-utils/       # Test helpers & stubs
├── infrastructure/       # Container & local dev configs
├── scripts/              # Cross-platform setup scripts
├── docs/                 # Product & Architecture docs
└── tests/                # Global E2E & integration test suites
```
