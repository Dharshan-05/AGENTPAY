# AGENTPAY MASTER DESIGN SYSTEM & UI CONTRACT v1.0

## 1. Overview
The **AGENTPAY Design System** establishes a unified visual identity, UI architecture, component library, and design tokens across all production operational modules.

---

## 2. Core Color Palette & Design Tokens

### Background Surfaces
* **Canvas Background**: `var(--ag-background)` — `#020617` (Obsidian Black)
* **Surface Panel**: `var(--ag-surface)` — `#090D16` (Deep Slate)
* **Elevated Surface**: `var(--ag-surface-elevated)` — `#0F172A` (Slate 900)
* **Interactive Hover Surface**: `var(--ag-surface-hover)` — `#1E293B` (Slate 800)

### Hairlines & Borders
* **Hairline Border**: `var(--ag-border)` — `rgba(255, 255, 255, 0.08)`
* **Active/Selected Border**: `var(--ag-border-strong)` — `rgba(255, 255, 255, 0.15)`

### Brand & Status Accents
* **Trust Emerald** (`#10B981`): Operational status, valid authorization, success.
* **Shield Amber** (`#F59E0B`): Pending reviews, velocity warnings, medium risk.
* **Alert Crimson** (`#EF4444`): Policy violations, blocked attempts, critical risk.
* **Sovereign Blue** (`#3B82F6`): Infrastructure, secondary navigation, intent parsing.
* **Neural Violet** (`#8B5CF6`): AI telemetry, LLM router status.

---

## 3. Typography Hierarchy

* **Display Font**: `Space Grotesk, sans-serif` — Page Titles, Major Metrics, Logos.
* **Body Font**: `Inter, sans-serif` — Subtitles, Descriptions, Card Content.
* **Telemetry Font**: `JetBrains Mono, monospace` — Badges, Hashes, Code, Timestamps, Table Data.

---

## 4. Master Layout Architecture (`AgentPayShell`)

Every production dashboard route is wrapped inside `components/layout/AgentPayShell.tsx`:

```
┌─────────────────────────────────────────────────────────────┐
│ AGENTPAY TOP NAV (AgentPayTopNav.tsx)                       │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  SIDEBAR     │            PAGE CONTENT AREA                 │
│(AgentPay     │           (PageHeader + Grid)                │
│ Sidebar.tsx) │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

---

## 5. Reusable Component Contracts

### Buttons (`AGButton`)
Variants: `primary`, `secondary`, `ghost`, `danger`, `warning`, `success`, `outline`.

### Badges (`AGBadge`)
Standardized statuses: `ACTIVE`, `AUTHORIZED`, `APPROVED`, `PENDING`, `REVIEW`, `BLOCKED`, `HIGH_RISK`, `LOW_RISK`, `POLICY_SECURE`, `LIVE`.

### Cards (`AGCard`, `AGMetricCard`, `AGGlassCard`, `AGStatusCard`)
Uniform 16px border-radius, hairline borders, backdrop blur, and hover state transitions.

### Data Tables (`AGTable`)
Standardized monospace table styling with selectable row states and risk score badges.

---

## 6. Production Route Registry

1. `001 /` — AGENTPAY Landing Page
2. `002 /command-center` — Operations & Fleet Command Center
3. `003 /ai-command-center` — Natural Language AI Command Center
4. `004 /agentguard` — Autonomous Policy & Governance Center
5. `005 /fraudguard` — AI Risk & Anomaly Intelligence
6. `006 /payments` — Payment Processing Rails
7. `007 /analytics` — Cross-Agent Analytics & Telemetry
8. `008 /developers` — Developer API & SDK Integration
9. `009 /settings` — Platform Configuration & Governance Controls
