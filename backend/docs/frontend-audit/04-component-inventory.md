# 04 — Component Inventory & Reuse Matrix

| Component Name | Source File | Purpose | Used By | Reusable? | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Sidebar` | `components/layout/Sidebar.tsx` | Main navigation sidebar | Layout | Yes | **KEEP** |
| `Header` | `components/layout/Header.tsx` | Top navbar with search & notifications | Layout | Yes | **KEEP** |
| `PageHeader` | `components/layout/PageHeader.tsx` | Page title, breadcrumbs, actions | All Pages | Yes | **KEEP** |
| `StatCard` | `components/ui/StatCard.tsx` | KPI metric tile with trend | Overview, Risk, Settl | Yes | **KEEP** |
| `DataTable` | `components/tables/DataTable.tsx` | Sortable, paginated data table | Payments, Settl | Yes | **KEEP** |
| `StatusBadge` | `components/ui/StatusBadge.tsx` | Status pill indicator | All Pages | Yes | **KEEP** |
| `RiskScoreGauge` | `components/ui/RiskScoreGauge.tsx` | Threat score gauge | Risk, Details | Yes | **KEEP** |
| `FilterToolbar` | `components/ui/FilterToolbar.tsx` | Filter toolbar with search | Payments, Settl | Yes | **KEEP** |
| `LoadingState` | `components/feedback/LoadingState.tsx` | Loading skeleton spinner | Feedback | Yes | **KEEP** |
| `EmptyState` | `components/feedback/EmptyState.tsx` | Zero-data placeholder | Feedback | Yes | **KEEP** |
