'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { BarChart3, RefreshCw, Download, FileText, Cpu } from 'lucide-react';

interface AnalyticsHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onGenerateReport: () => void;
}

export function AnalyticsHeader({ onRefresh, onExport, onGenerateReport }: AnalyticsHeaderProps) {
  return (
    <PageHeader
      eyebrow="ENTERPRISE TRANSACTION INTELLIGENCE & OPERATIONAL ANALYTICS"
      title="ANALY"
      highlightTitle="TICS"
      description="Enterprise transaction intelligence, agent performance, risk telemetry, payment trends, and operational decision analytics."
      icon={BarChart3}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ANALYTICS ENGINE ONLINE (v2.4)
        </span>
      }
      actions={
        <>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span>ENGINE:</span>
            <span className="text-blue-400 font-bold">ANALYTICS-ENGINE-v2.4</span>
          </div>
          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Data
          </AGButton>
          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Analytics
          </AGButton>
          <AGButton variant="primary" size="md" icon={FileText} onClick={onGenerateReport}>
            Generate Report
          </AGButton>
        </>
      }
    />
  );
}
