# TABLE SYSTEM AUDIT

## DATA TABLE CONSISTENCY
- **Table Container**: `p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto`
- **Table Header Row**: `border-b border-white/[0.08] text-[10px] text-slate-500 uppercase font-mono`
- **Table Data Row**: `border-b border-white/[0.04] hover:bg-slate-900/40 cursor-pointer transition-colors`
- **Cell Padding**: `p-3` across 95% of tables.
- **Monospace Alignments**: Transaction IDs, amounts, latency MS, hashes, and dates aligned in `font-mono`.

## MINOR ISSUES
- Custom horizontal scrollbar styling missing on 3 tables (`/transactions`, `/approvals`, `/fraudguard`), relying on browser default dark scrollbar.
