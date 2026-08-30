'use client';

import { AGCard } from '@/components/ui/ag-card';
import { FraudSignalRecord } from './analytics-types';
import { Cpu, ExternalLink, Sparkles } from 'lucide-react';
import Link from 'next/link';

interface FraudAnalyticsProps {
  signals: FraudSignalRecord[];
}

export function FraudAnalytics({ signals }: FraudAnalyticsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Cpu className="w-4 h-4 text-purple-400" />
          <span className="text-sm">FRAUDGUARD SIGNAL INTELLIGENCE</span>
        </div>
        <Link href="/fraudguard" className="text-[10px] text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1">
          FRAUDGUARD <ExternalLink className="w-3 h-3" />
        </Link>
      </div>

      <div className="grid grid-cols-4 gap-2 text-[11px]">
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Signals Detected</span>
          <span className="font-bold text-amber-400">1,482</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">High Risk Cases</span>
          <span className="font-bold text-red-400">12</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">False Positive Est.</span>
          <span className="font-bold text-emerald-400">2.8%</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
          <span className="text-[10px] text-slate-400 block">Resolution Rate</span>
          <span className="font-bold text-blue-400">94.2%</span>
        </div>
      </div>

      <div className="space-y-3">
        <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          RISK CONTRIBUTION VECTOR BREAKDOWN
        </h4>

        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.04] space-y-3 text-[11px]">
          {signals.map((sig) => (
            <div key={sig.name} className="space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-200 font-semibold">{sig.name}</span>
                <span className="text-amber-400 font-bold">+{sig.contribution} Score</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                <div
                  className="h-full rounded-full bg-purple-500 transition-all"
                  style={{ width: `${sig.contribution * 2.5}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </AGCard>
  );
}
