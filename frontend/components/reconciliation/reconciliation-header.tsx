'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { Scale, RefreshCw, Download, Play } from 'lucide-react';

interface ReconciliationHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onRunReconciliation: () => void;
}

export function ReconciliationHeader({ onRefresh, onExport, onRunReconciliation }: ReconciliationHeaderProps) {
  return (
    <PageHeader
      eyebrow="ZERO-TRUST FINANCIAL CLEARING & DISPUTE ARBITRATION CONTROL PLANE"
      title="RECON"
      highlightTitle="CILIATION"
      description="Settlement intelligence, variance control, chargeback operations, and immutable financial audit."
      icon={Scale}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ● RECONCILIATION ENGINE ONLINE (v1.8)
        </span>
      }
      actions={
        <>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span className="text-slate-400 font-bold">HASH CHAIN:</span>
            <span className="text-emerald-400 font-bold">VERIFIED</span>
          </div>

          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Feed
          </AGButton>

          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Audit Ledger
          </AGButton>

          <AGButton variant="primary" size="md" icon={Play} onClick={onRunReconciliation}>
            RUN RECONCILIATION
          </AGButton>
        </>
      }
    />
  );
}
