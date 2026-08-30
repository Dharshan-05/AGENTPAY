'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { CreditCard, RefreshCw, Download, Plus, Zap } from 'lucide-react';

interface PaymentHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onCreatePayment: () => void;
}

export function PaymentHeader({ onRefresh, onExport, onCreatePayment }: PaymentHeaderProps) {
  return (
    <PageHeader
      eyebrow="FINANCIAL TRANSACTION EXECUTION & SETTLEMENT TELEMETRY"
      title="PAY"
      highlightTitle="MENTS"
      description="Financial transaction execution, settlement, payout and payment telemetry."
      icon={CreditCard}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          LIVE PAYMENT ENGINE ONLINE
        </span>
      }
      actions={
        <>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span>ENGINE:</span>
            <span className="text-blue-400 font-bold">PAY-ENGINE-v2.4</span>
          </div>
          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Feed
          </AGButton>
          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Audit Logs
          </AGButton>
          <AGButton variant="primary" size="md" icon={Plus} onClick={onCreatePayment}>
            Create Payment
          </AGButton>
        </>
      }
    />
  );
}
