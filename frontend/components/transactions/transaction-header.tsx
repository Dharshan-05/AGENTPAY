'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGButton } from '@/components/ui/ag-button';
import { Receipt, RefreshCw, Download } from 'lucide-react';

interface TransactionHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
}

export function TransactionHeader({ onRefresh, onExport }: TransactionHeaderProps) {
  return (
    <PageHeader
      eyebrow="PAYMENT INTENT + TRANSACTION LIFECYCLE CONTROL PLANE"
      title="TRANSACTION"
      highlightTitle="OPERATIONS"
      description="Autonomous agent payment intent lifecycle, authorization state, processor routing, settlement tracking, and immutable financial audit for every AI-originated transaction."
      icon={Receipt}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ● TRANSACTION ENGINE ONLINE
        </span>
      }
      actions={
        <>
          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Telemetry
          </AGButton>

          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Ledger
          </AGButton>
        </>
      }
    />
  );
}
