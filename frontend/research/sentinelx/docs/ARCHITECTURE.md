# SentinelX — System Architecture

## Request flow

```mermaid
flowchart LR
    U[Employee / App] -->|HTTP POST /api/scan| GW[Fastify Gateway]
    GW --> IN[1. Inspector Agent]
    IN --> SD[2. Secret Detection Agent]
    SD --> PE[3. Policy Engine Agent]
    PE --> RE[4. Risk Engine Agent]
    RE -->|CRITICAL / HIGH| RW[5. Rewriter Agent]
    RE -->|SAFE / MEDIUM| RW
    RW --> LA[6. LLM Adapter Agent]
    LA --> AL[7. Audit Logger Agent]
    AL --> ME[8. Memory Agent]
    AL --> DB[(Audit Store)]
    DB --> UI[Dashboard / Audit / Reports]
```

## Decision engine

```mermaid
flowchart TD
    P[Prompt] --> D[42 detection rules]
    D -->|secret found| SEV[Severity: CRITICAL/HIGH/MEDIUM/LOW/INFO]
    SEV --> OVERLAP[Dedupe overlaps: higher severity wins, ties = longest match]
    OVERLAP --> RISK[Composite risk score 0-100]
    RISK -->|>= 80| BLOCK[BLOCK - incident raised]
    RISK -->|>= 50| REW[REWRITE - sanitize + flag]
    RISK -->|>= 15| FLAG[ALLOW with FLAG]
    RISK -->|< 15| OK[ALLOW - SAFE]
    P --> POL[Policy packs: GDPR/HIPAA/PCI/SOC2/ISO27001/Internal/Secrets]
    POL --> RISK
```

## Data layer

```mermaid
erDiagram
    USER ||--o{ AUDITLOG : produces
    USER ||--o{ ALERT : triggers
    AUDITLOG {
        string id
        string userId
        string prompt
        string finalPrompt
        string decision
        int riskScore
        json violations
        json secrets
        json agentTrace
    }
    POLICY ||--o{ DETECTIONRULE : contains
    POLICY {
        string id
        string name
        string regulation
        string enforcement
    }
    DETECTIONRULE {
        string id
        string policyId
        string name
        string pattern
        string severity
    }
```

## Deployment modes

- **Demo (default)**: no external services. `src/lib/store.ts` detects Postgres availability and falls back to an in-memory store, seeded on boot. Redis cache disabled.
- **Enterprise**: set `DATABASE_URL` + `REDIS_URL` in `apps/api/.env`; Prisma migrations apply, caching and dedupe enable automatically.
