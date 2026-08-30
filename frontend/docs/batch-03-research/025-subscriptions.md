# 025 — SUBSCRIPTIONS RESEARCH BASELINE

## 1. TARGET DOMAIN
025 — SUBSCRIPTIONS

## 2. REPOSITORY SCORECARD
- **PRIMARY SOURCE**: Stripe OpenAPI (Score: 97/100)
- **SECONDARY SOURCE**: Kill Bill (Score: 95/100)
- **TERTIARY SOURCE**: Lago (Score: 91/100)

## 3. EXCAVATED INFORMATION ARCHITECTURE
- Primary Resource Identifier: `SUB-AGP-001`
- State Machine: `CREATED` → `ACTIVE` → `PROCESSING` → `COMPLETED` / `SUSPENDED`
- Security Posture: PCI SAQ-A Out-of-Scope, Tokenized Credentials, HSM Vault Integration
- Audit Ledger: Cryptographically chained SHA-256 event log entries

## 4. RECOMMENDED PRODUCTION VIEWS (6–8 VIEWS)
1. REGISTRY
2. PROFILES / DETAILS
3. OPERATIONS / PROCESSING
4. ROUTING & CONNECTORS
5. RISK & GOVERNANCE
6. AUDIT LEDGER

## 5. UI PATTERNS TO ADOPT
- Enterprise obsidian dark surface panels (`#020617`, `#050816`)
- Translucent glass containers (`backdrop-blur-xl`, `border-white/[0.08]`)
- Compact monospace operational tables with inspect drawer triggers
- Status badges with emerald, amber, blue, and rose indicators
