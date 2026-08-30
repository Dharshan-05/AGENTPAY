# 083 — FX EXCHANGES RESEARCH BASELINE

## 1. TARGET DOMAIN
083 — FX EXCHANGES

## 2. PRODUCTION ROUTE
`/fx-exchanges`

## 3. REPOSITORY SCORECARD
- **PRIMARY SOURCE**: Apache Fineract (Score: 98/100)
- **SECONDARY SOURCE**: Stripe OpenAPI (Score: 96/100)
- **TERTIARY SOURCE**: ERPNext (Score: 93/100)

## 4. EXCAVATED INFORMATION ARCHITECTURE
- Primary Resource Identifier: `FXEX-AGP-001`
- State Machine: `INITIALIZED` → `ACTIVE` → `PROCESSING` → `VERIFIED` / `COMPLETED`
- Security Posture: Masked Identifiers, Tokenized Attributes, PCI SAQ-A Compliance
- Audit Ledger: Cryptographically chained event log entries

## 5. RECOMMENDED PRODUCTION VIEWS (6–8 VIEWS)
1. REGISTRY
2. PROFILES / DETAILS
3. OPERATIONS / EXECUTION
4. ROUTING & CONNECTORS
5. RISK & GOVERNANCE
6. AUDIT LEDGER

## 6. UI PATTERNS TO ADOPT
- Enterprise obsidian dark surface panels (`#020617`, `#050816`)
- Translucent glass containers (`backdrop-blur-xl`, `border-white/[0.08]`)
- Compact monospace operational tables with inspect drawer triggers
- Status badges with emerald, amber, blue, and rose indicators
