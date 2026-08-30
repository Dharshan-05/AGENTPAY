# AGENTPAY — 46: Root Monorepo Orchestration Commands (`package.json` scripts)

## 1. Master Workspace Commands

```json
{
  "scripts": {
    "dev": "turbo run dev --parallel",
    "build": "turbo run build",
    "test": "vitest run",
    "test:unit": "vitest run --selectProjects unit",
    "test:integration": "vitest run --selectProjects integration",
    "lint": "eslint \"**/*.{ts,tsx}\"",
    "typecheck": "tsc --build",
    "format": "prettier --write \".\"",
    "format:check": "prettier --check \".\"",
    "db:migrate": "pnpm --filter @agentpay/database db:migrate",
    "db:seed": "pnpm --filter @agentpay/database db:seed"
  }
}
```
