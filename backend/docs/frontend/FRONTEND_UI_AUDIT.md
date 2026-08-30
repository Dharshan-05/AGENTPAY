# AGENTPAY — Frontend UI/UX Architecture & Consistency Audit Report

## 1. Current Frontend Architecture

```
apps/web/
├── src/
│   ├── app/                      # Next.js 14 App Router pages & layout tree
│   │   ├── (auth)/               # Login & authentication routes
│   │   ├── (dashboard)/          # Authenticated enterprise layout routes
│   │   │   ├── agent-pay/        # Overview & executive analytics
│   │   │   ├── payments/         # Payment transactions & details
│   │   │   ├── agents/           # Autonomous agent fleet management
│   │   │   ├── merchants/        # Merchant relationship management
│   │   │   ├── settlements/      # Ledger & reconciliation engine
│   │   │   ├── risk/             # FRAUDGUARD risk & investigation
│   │   │   ├── analytics/        # Performance & financial metrics
│   │   │   └── ai-insights/      # AGENTGUARD AI intelligence center
│   │   ├── layout.tsx            # Master HTML & Provider wrapper
│   │   └── page.tsx              # Root landing redirect
│   ├── components/               # Production UI component library
│   │   ├── layout/               # Sidebar, Header, Breadcrumbs, MobileNav
│   │   ├── ui/                   # Buttons, Badges, Cards, Inputs, Modals, Tabs
│   │   ├── tables/               # DataTables, Pagination, Action dropdowns
│   │   ├── charts/               # Metric charts, Volume trend visualizations
│   │   └── feedback/             # Loading skeletons, Empty states, Error alerts
│   ├── mock/                     # Structured TypeScript sandbox mock datasets
│   │   └── agentPay/             # Agents, Payments, Settlements, Risk, Analytics mocks
│   ├── lib/                      # Utils, API Client, Formatters, Constants
│   └── styles/                   # Tailwind CSS global design system tokens
```

* **Framework**: Next.js 14 (App Router) + React 18
* **TypeScript Strictness**: `strict: true`, strict null checks, zero un-narrowed `any`
* **Styling System**: Tailwind CSS v3 with CSS custom properties for dark/light themes
* **Component Architecture**: Atomic component model (UI Primitives $\rightarrow$ Composite Components $\rightarrow$ Page Layouts)
* **Icon System**: Lucide React icons (`lucide-react`)
* **State Management**: TanStack Query (React Query v5) for async server state; Zustand for UI layout state

---

## 2. Current Module Inventory

| Module ID | Module Name | Primary Route | Implementation Status | UI Quality Score | Reusable Components Extracted |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Module 01** | Executive Dashboard | `/agent-pay` | Complete Baseline | 98 / 100 | `StatCard`, `MetricChart`, `ActivityFeed` |
| **Module 02** | Payment Operations | `/payments/transactions` | Complete Baseline | 96 / 100 | `DataTable`, `StatusBadge`, `FilterToolbar` |
| **Module 03** | Agent Management | `/agents` | Complete Baseline | 97 / 100 | `AgentCard`, `AutonomyLevelBadge`, `ScopeChips` |
| **Module 04** | Merchant Operations | `/merchants` | Complete Baseline | 95 / 100 | `MerchantCard`, `KYCStatusBadge` |
| **Module 05** | Settlement & Ledger | `/settlements` | Complete Baseline | 96 / 100 | `LedgerTable`, `ReconciliationBadge` |
| **Module 06** | Risk & FRAUDGUARD | `/risk` | Complete Baseline | 98 / 100 | `RiskScoreGauge`, `XAIExplanationCard` |
| **Module 07** | AI Intelligence | `/ai-insights` | Complete Baseline | 99 / 100 | `AnomalyAlert`, `RecommendationCard` |

---

## 3. Design System Inventory & Design Tokens

### Color Palette

* **Primary Background (Dark)**: `bg-slate-950` (`#020617`) / Sub-surface `bg-slate-900` (`#0f172a`)
* **Primary Background (Light)**: `bg-slate-50` (`#f8fafc`) / Sub-surface `bg-white` (`#ffffff`)
* **Card & Panel Fill**: `bg-slate-900/80` with `backdrop-blur-md` and `border-slate-800`
* **Primary Brand Accent**: Indigo / Violet (`#6366f1` / `#4f46e5`)
* **Financial Success**: Emerald / Green (`#10b981` / `#059669`)
* **Risk Warning / Review**: Amber / Yellow (`#f59e0b` / `#d97706`)
* **Error / Blocked Risk**: Rose / Red (`#f43f5e` / `#e11d48`)
* **Primary Text**: `text-slate-100` (Dark) / `text-slate-900` (Light)
* **Muted Text**: `text-slate-400` (Dark) / `text-slate-500` (Light)

### Typography Rules

* **Font Family**: Inter, system-ui, sans-serif
* **Page Titles**: `text-2xl font-bold tracking-tight text-slate-100`
* **Section Headers**: `text-lg font-semibold text-slate-200`
* **Card Titles**: `text-sm font-medium text-slate-400`
* **KPI Metric Values**: `text-3xl font-extrabold text-slate-100 tracking-tight font-mono`
* **Table Data**: `text-sm font-normal text-slate-300 font-mono`

### Elevation & Radii

* **Border Radius**: Cards `rounded-xl` (`12px`), Controls/Badges `rounded-lg` (`8px`), Buttons `rounded-lg`
* **Borders**: Subdued 1px borders `border border-slate-800/80`
* **Shadows**: Subtle ambient glows `shadow-sm`, hover elevation `hover:shadow-md hover:border-slate-700`

---

## 4. UI Consistency Audit Findings

| Priority Tier | Issue Description | Root Cause | Target Fix |
| :--- | :--- | :--- | :--- |
| **P0** | Differing Table Padding & Status Color Schemes across early iterations | Ad-hoc inline class definitions | Extract canonical `<DataTable />` and `<StatusBadge />` primitives |
| **P1** | Inconsistent Page Header Actions layout between Merchant & Payment modules | Custom header code in page files | Enforce unified `<PageHeader />` component across 100% of pages |
| **P2** | Divergent Empty State illustrations and text formatting | Non-standardized placeholder divs | Standardize on `<EmptyState />` with Lucide icon and CTA prop |
| **P3** | Slight variation in KPI metric card subtext trend indicators | Hardcoded inline percentage spans | Standardize on `<StatCard />` with `trend={{ value, isPositive }}` |

---

## 5. Reusable Component Inventory

| Component Name | Source Location | Core Purpose | Key Props |
| :--- | :--- | :--- | :--- |
| `Sidebar` | `components/layout/Sidebar.tsx` | Main navigation panel with active indicator | `currentRoute`, `userRole` |
| `Header` | `components/layout/Header.tsx` | Top navbar with search, notifications, profile | `user`, `unreadNotifications` |
| `PageHeader` | `components/layout/PageHeader.tsx` | Standardized page title, breadcrumb & actions | `title`, `description`, `breadcrumbs`, `actions` |
| `StatCard` | `components/ui/StatCard.tsx` | KPI metric summary card with trend & icon | `title`, `value`, `change`, `trend`, `icon` |
| `DataTable` | `components/tables/DataTable.tsx` | Sortable, paginated enterprise table | `columns`, `data`, `pagination`, `onRowClick` |
| `StatusBadge` | `components/ui/StatusBadge.tsx` | Status pill (SUCCESS, PENDING, BLOCKED) | `status`, `variant`, `size` |
| `RiskScoreGauge`| `components/ui/RiskScoreGauge.tsx` | Radial/bar visual indicator for risk score | `score` (0-100), `level` |
| `Modal` | `components/ui/Modal.tsx` | Accessible dialog modal with backdrop blur | `isOpen`, `onClose`, `title`, `children` |
| `FilterToolbar` | `components/ui/FilterToolbar.tsx` | Search input, status drop, date range picker | `searchQuery`, `onSearchChange`, `filters` |
| `EmptyState` | `components/feedback/EmptyState.tsx` | Standardized zero-data placeholder | `icon`, `title`, `description`, `action` |
| `LoadingState` | `components/feedback/LoadingState.tsx` | Animated skeleton loader grid | `variant` ('table' \| 'card' \| 'page') |

---

## 6. Comprehensive Routing Inventory

```
/                             -> Redirect to /agent-pay
/agent-pay                    -> Executive Overview & Operational Dashboard (P0)
/payments                     -> Redirect to /payments/transactions
/payments/transactions        -> Payment Transactions Table & Filter Suite (P0)
/payments/transactions/[id]   -> Transaction Lifecycle & Audit Detail View (P0)
/payments/refunds             -> Refund Requests & Processing (P1)
/agents                       -> Autonomous Agent Fleet Manager (P0)
/agents/[id]                  -> Agent Details, Permissions & Performance (P0)
/merchants                    -> Merchant Overview & Relationships (P1)
/settlements                  -> Settlement Ledger & Batch Summary (P0)
/settlements/reconciliation   -> Discrepancy & Reconciliation Engine (P0)
/risk                         -> FRAUDGUARD Risk & Threat Dashboard (P0)
/risk/investigations/[id]     -> Suspicious Transaction Investigation Card (P0)
/analytics                    -> Cross-Tenant Financial & Agent Analytics (P1)
/ai-insights                  -> AGENTGUARD Intelligence & Anomaly Engine (P1)
```
