'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGButton } from '@/components/ui/ag-button';
import { Bot, RefreshCw, Download, Plus } from 'lucide-react';

interface AgentHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  onRegister: () => void;
}

export function AgentHeader({ onRefresh, onExport, onRegister }: AgentHeaderProps) {
  return (
    <PageHeader
      eyebrow="ZERO-TRUST AUTONOMOUS AGENT IDENTITY & OPERATIONS CONTROL PLANE"
      title="AGENT REG"
      highlightTitle="ISTRY & OPERATIONS"
      description="First-class AI security identities, RBAC capabilities, durable execution tracking, and mTLS security posture."
      icon={Bot}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ● AGENT OPERATIONS ONLINE (v2.1)
        </span>
      }
      actions={
        <>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span className="text-slate-400 font-bold">IDENTITY:</span>
            <span className="text-emerald-400 font-bold">ZERO-TRUST VERIFIED</span>
          </div>

          <AGButton variant="ghost" size="md" icon={RefreshCw} onClick={onRefresh}>
            Refresh Telemetry
          </AGButton>

          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Agent Ledger
          </AGButton>

          <AGButton variant="primary" size="md" icon={Plus} onClick={onRegister}>
            REGISTER AGENT
          </AGButton>
        </>
      }
    />
  );
}
