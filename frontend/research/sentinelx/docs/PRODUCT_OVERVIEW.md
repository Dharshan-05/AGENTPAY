# SentinelX — Product Overview

**SentinelX** is an enterprise AI Security platform (AI Governance Firewall) that sits between users and LLM providers. It inspects every prompt through an 8-agent pipeline, detects sensitive data (credentials, PII, PHI, card data), evaluates policy compliance (GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001), scores risk, and either blocks, rewrites, or allows the request — with full explainability and a tamper-evident audit trail.

## Why it exists

Organizations are deploying generative AI without guardrails. Employees paste AWS keys, salary sheets, patient records, and source code into public models — an uncontrolled data exfiltration vector. SentinelX makes AI usage safe, auditable, and demonstrable to regulators.

## Core value proposition

- **Block before it leaves** — credentials and PII never reach the model.
- **Every decision explainable** — why, how, which rule, what confidence, what alternative.
- **Enterprise telemetry** — executive, SOC, twin, analytics, and system views from one deployment.
- **Demo-ready** — a one-click demo and a keynote-style Judge Presentation Mode.

## The 8-agent pipeline

| # | Agent | Responsibility |
|---|-------|----------------|
| 1 | Inspector Agent | Classifies intent & data sensitivity |
| 2 | Secret Detection Agent | 30+ deterministic pattern rules |
| 3 | Policy Engine | 5 regulation packs evaluated per request |
| 4 | Risk Engine | Composite risk score 0–100 |
| 5 | Prompt Rewriter | Intent-preserving sanitisation |
| 6 | LLM Adapter | Multi-provider gateway routing |
| 7 | Audit Logger | Tamper-evident audit record |
| 8 | Memory Agent | Session & behavioural context |

Decision matrix: **BLOCK** (critical), **REWRITE** (high/medium), **FLAG** (low), **ALLOW** (safe).

## Product areas

| Area | Route | Purpose |
|------|-------|---------|
| Prompt Scanner | `/scanner` | Live pipeline with replay controls + trace export |
| Demo Mode | `/demo` | One-click attack sequence + Judge Presentation Mode |
| Executive Command Center | `/executive` | Security score, maturity, KPIs, recommendations |
| Security Operations Center | `/soc` | Global threat feed, attack lifecycle, threat ticker, throughput, live counters |
| Digital Twin | `/twin` | Interactive org risk graph (6 departments) + department DNA |
| Enterprise Analytics | `/analytics` | 15 charts (incl. risk forecast, incident heatmap, policy effectiveness, detection accuracy, compliance trend), brush zoom, CSV/PNG export |
| AI Copilot | `/copilot` | Executive + security telemetry assistant with rich answer cards |
| AI Explainability Center | `/explain` | Decision corpus: agent contributions, reasoning timeline, risk/policy factors, confidence, recommendation |
| Incident Investigation | `/incidents/[id]` | Full decision chain + report download |
| Enterprise Settings | `/settings` | Policy builder + templates, notifications, API tokens, roles, branding, export |
| System & Infrastructure | `/system` | Deployment health, cluster telemetry |

## Technical summary

- **API**: Node.js + Fastify, 8 rule-based agents, in-memory demo store with optional PostgreSQL.
- **Web**: Next.js 16 (App Router) + React 19 + TypeScript (strict) + Framer Motion + Recharts.
- **Design system**: dark glass cards, accent `#0B827A`, Inter + JetBrains Mono, `MotionConfig reducedMotion="user"`.
- **Quality gate**: zero TS errors, zero ESLint errors, zero build/runtime errors, zero hydration warnings.

## Status

Phase 6 complete — production experience layer shipped. The platform is feature-complete for a national AI hackathon demonstration and judge presentation.
