# 01 — Frontend Architecture Specification

## 1. Overview & Framework Stack
* **Framework**: Next.js 14 (App Router) + React 18
* **Language**: TypeScript (Strict Mode)
* **Styling**: Tailwind CSS v3 + CSS Custom Properties for theme tokens
* **Icon System**: Lucide React (`lucide-react`)
* **State Management**: TanStack React Query v5 for server state; React State for UI controls
* **Routing**: Next.js File-system App Router (`apps/web/src/app`)

---

## 2. Directory Layout & App Structure

```text
apps/web/src/
├── app/                      # App Router routes & layouts
│   ├── (dashboard)/          # Authenticated enterprise layout shell
│   └── layout.tsx            # Master HTML & Tailwind global provider
├── components/               # Production component library
│   ├── layout/               # Sidebar, Header, PageHeader
│   ├── ui/                   # StatCard, StatusBadge, RiskScoreGauge, FilterToolbar
│   ├── tables/               # DataTable & Pagination
│   └── feedback/             # LoadingState, EmptyState
├── mock/                     # Typed TypeScript mock datasets
│   └── agentPay/             # agents.ts, payments.ts, settlements.ts, risk.ts, analytics.ts
└── styles/                   # globals.css
```
