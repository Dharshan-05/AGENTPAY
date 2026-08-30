'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldAlert, Sparkles, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export function RiskIntelligence() {
  return (
    <AGCard className="space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs">
        <span className="font-bold text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400" /> RISK INTELLIGENCE
        </span>
        <Link href="/fraudguard" className="text-[10px] text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
          FRAUDGUARD <ExternalLink className="w-3 h-3" />
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-2 font-mono text-xs">
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block uppercase">AVG RISK SCORE</span>
          <span className="text-xl font-bold text-amber-400">56.4 / 100</span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block uppercase">PEAK RISK SCORE</span>
          <span className="text-xl font-bold text-red-400">96 / 100</span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block uppercase">BLOCKED TXNS</span>
          <span className="text-xl font-bold text-red-400">42</span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block uppercase">MANUAL REVIEWS</span>
          <span className="text-xl font-bold text-amber-400">18</span>
        </div>
      </div>

      {/* Risk Band Distribution Bar */}
      <div className="space-y-2 font-mono text-xs">
        <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">
          RISK BAND DISTRIBUTION
        </span>

        <div className="h-3 w-full rounded-full bg-slate-950 overflow-hidden flex">
          <div className="h-full bg-emerald-500" style={{ width: '82%' }} title="Low Risk 82%" />
          <div className="h-full bg-amber-500" style={{ width: '14%' }} title="Medium Risk 14%" />
          <div className="h-full bg-red-500" style={{ width: '4%' }} title="High/Critical Risk 4%" />
        </div>

        <div className="flex justify-between text-[10px] text-slate-400">
          <span className="text-emerald-400 font-bold">● LOW (1,422)</span>
          <span className="text-amber-400 font-bold">● MED (48)</span>
          <span className="text-red-400 font-bold">● HIGH (12)</span>
        </div>
      </div>
    </AGCard>
  );
}
