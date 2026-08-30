# COMPONENT CONSISTENCY AUDIT

## SHARED PRIMITIVES REUSE ASSESSMENT

1. **`AgentPayShell`**: Used on 104/104 production routes (100% compliance). Wraps sidebar & top bar.
2. **`AgentPaySidebar`**: Single source of navigation truth with 104 active navigation badges (`001` to `104`).
3. **`PageHeader`**: Used on 104/104 pages with eyebrow, title, highlightTitle, description, icon, statusBadge, actions.
4. **`AGMetricCard`**: Used across 104/104 pages in 4–6 grid layout for high-density KPI summaries.
5. **`AGButton`**: Standardized variant system (`primary`, `secondary`, `ghost`, `danger`) with size controls (`sm`, `md`, `lg`).
6. **`AGBadge`**: Color-coded status badges (`SETTLED`, `ACTIVE`, `BLOCKED`, `VERIFIED`, `PENDING`).
7. **`AGDrawer`**: Slide-over drawer primitive with backdrop blur, title, subtitle, footer, and ESC key listener.

## IDENTIFIED MINOR VARIANCES
- Early pages (Batches 01–03) use inline custom filter wrappers before `AGButton` ghost filters were standardized in Batch 04.
- Table headers in early pages use `text-[10px]` while later pages use `text-xs font-mono uppercase tracking-wider`.
