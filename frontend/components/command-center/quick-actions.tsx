'use client';

import { Shield, Plus, Lock, RefreshCw, Sliders, AlertOctagon } from 'lucide-react';
import { Magnetic } from '@/components/motion/magnetic';

interface QuickActionsProps {
  onAddAgent: () => void;
  onNewPolicy: () => void;
  onRefreshData: () => void;
  onToggleFreeze: () => void;
}

export function QuickActions({
  onAddAgent,
  onNewPolicy,
  onRefreshData,
  onToggleFreeze,
}: QuickActionsProps) {
  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-4 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <Sliders className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
          COMMAND QUICK ACTIONS
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Magnetic strength={8}>
          <button
            onClick={onAddAgent}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-mono text-xs font-semibold hover:bg-emerald-500/30 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            Provision Agent Identity
          </button>
        </Magnetic>

        <Magnetic strength={8}>
          <button
            onClick={onNewPolicy}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-white/10 text-slate-200 font-mono text-xs font-medium hover:bg-slate-800 hover:border-emerald-500/30 transition-all"
          >
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            Add AGENTGUARD Rule
          </button>
        </Magnetic>

        <Magnetic strength={8}>
          <button
            onClick={onRefreshData}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-white/10 text-slate-300 font-mono text-xs font-medium hover:bg-slate-800 hover:text-white transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5 text-blue-400" />
            Sync Telemetry
          </button>
        </Magnetic>

        <button
          onClick={onToggleFreeze}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-xs font-semibold hover:bg-red-500/20 transition-all"
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          Emergency Freeze
        </button>
      </div>
    </div>
  );
}
