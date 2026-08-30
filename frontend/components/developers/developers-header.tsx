'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { Code2, RefreshCw, Download, Plus, Key } from 'lucide-react';

interface DevelopersHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onCreateKey: () => void;
}

export function DevelopersHeader({ onRefresh, onExport, onCreateKey }: DevelopersHeaderProps) {
  return (
    <PageHeader
      eyebrow="ZERO-TRUST AGENT CREDENTIAL & DEVELOPER SECURITY CONSOLE"
      title="DEVEL"
      highlightTitle="OPERS"
      description="API access, agent credentials, webhooks, SDK execution, and developer security telemetry."
      icon={Code2}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          DEVELOPER PLATFORM ONLINE
        </span>
      }
      actions={
        <>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span>ENGINE:</span>
            <span className="text-blue-400 font-bold">ANALYTICS-v2.4</span>
          </div>
          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Feed
          </AGButton>
          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Audit Logs
          </AGButton>
          <AGButton variant="primary" size="md" icon={Plus} onClick={onCreateKey}>
            CREATE API KEY
          </AGButton>
        </>
      }
    />
  );
}
