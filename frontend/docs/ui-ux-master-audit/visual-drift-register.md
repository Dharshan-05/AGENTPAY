# VISUAL DRIFT REGISTER

| ID | Route | Severity | Category | Issue Description | Recommended Fix (Step 2) |
|---|---|---|---|---|---|
| **DRIFT-001** | `/transactions` | P2 (Medium) | Table System | Default browser scrollbar visible on wide transaction table | Apply `scrollbar-thin scrollbar-thumb-slate-800` |
| **DRIFT-002** | `/approvals` | P2 (Medium) | Table System | Custom scrollbar missing on HITL queue table | Apply unified table scrollbar styling |
| **DRIFT-003** | `/fraudguard` | P2 (Medium) | Component | Single SHAP chart container padding differs by 4px from AGCard | Standardize `p-4` padding on SHAP container |
| **DRIFT-004** | `/` (Dashboard) | P3 (Low) | Typography | Header metric subtext uses `text-[11px]` instead of `text-xs` | Standardize subtext to `text-xs font-mono` |
| **DRIFT-005** | `/command-center` | P3 (Low) | Controls | Search reset button border opacity `border-white/10` vs `border-white/[0.08]` | Standardize border class to `border-white/[0.08]` |
| **DRIFT-006** | `/payments` | P3 (Low) | Component | Status badge font weight `font-medium` vs `font-bold` | Standardize badge font weight to `font-bold` |
| **DRIFT-007** | `/agents` | P3 (Low) | Table System | Table row hover background `hover:bg-slate-900/50` vs `hover:bg-slate-900/40` | Standardize hover background to `hover:bg-slate-900/40` |
| **DRIFT-008** | `/webhooks` | P3 (Low) | Typography | Endpoint URL monospace color `text-slate-400` vs `text-slate-300` | Standardize monospace endpoint text color |
| **DRIFT-009** | `/settings` | P4 (Obs) | Layout | Form section spacing `space-y-5` vs `space-y-6` | Align section spacing to `space-y-6` |
| **DRIFT-010** | `/checkout` | P4 (Obs) | Component | Embedded card container glow border on hover slightly brighter | Keep intentional for checkout focus affordance |
| **DRIFT-011** | `/reconciliation` | P4 (Obs) | Table System | Action button size in row `py-1` vs `py-1.5` | Standardize action button height |
| **DRIFT-012** | `/payment-methods` | P4 (Obs) | Component | Brand icon size `w-4 h-4` vs `w-3.5 h-3.5` | Standardize small icon size to `w-3.5 h-3.5` |
