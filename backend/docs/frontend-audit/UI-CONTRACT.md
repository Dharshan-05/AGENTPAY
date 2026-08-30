# AGENTPAY — UI CONTRACT & DESIGN SYSTEM SPECIFICATION

## 1. Master Shell & Container Layout
* **Master Layout**: `<DashboardLayout />` in `app/(dashboard)/layout.tsx`
* **Sidebar Nav**: 256px fixed width (`w-64`), dark surface `#0f172a` (`bg-slate-900`), 1px border `#1e293b` (`border-slate-800`).
* **Header Bar**: 64px fixed height (`h-16`), backdrop blur `bg-slate-900/80 backdrop-blur-md`.
* **Page Padding**: 24px (`p-6`), maximum container width `max-w-7xl`.

## 2. Reusable Component Rules
* **Page Headers**: `PageHeader.tsx` with title, optional description, breadcrumbs array, and right-aligned actions.
* **KPI Metrics**: `StatCard.tsx` with uppercase title, bold metric value, trend indicator, and Lucide icon badge.
* **Tables**: `DataTable.tsx` with uppercase header row, paginated navigation footer, and row-click navigation.
* **Status Indicators**: `StatusBadge.tsx` with color-coded status badges and iconography.
* **Risk Score Ratings**: `RiskScoreGauge.tsx` with threat score rating (0–100) and risk level tag.
