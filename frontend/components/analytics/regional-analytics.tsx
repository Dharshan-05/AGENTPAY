'use client';

import { AGCard } from '@/components/ui/ag-card';
import { RegionalActivityRecord } from './analytics-types';
import { Globe } from 'lucide-react';

interface RegionalAnalyticsProps {
  regions: RegionalActivityRecord[];
}

export function RegionalAnalytics({ regions }: RegionalAnalyticsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Globe className="w-4 h-4 text-blue-400" />
          <span className="text-sm">GLOBAL TRANSACTION INTELLIGENCE</span>
        </div>
        <span className="text-[10px] text-slate-400">Regional Matrix</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {regions.map((r) => (
          <div key={r.code} className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1.5">
            <div className="flex justify-between items-center text-[10px]">
              <span className="font-bold text-slate-100">{r.region}</span>
              <span className="text-blue-400 font-bold">{r.code}</span>
            </div>
            <div className="text-base font-bold text-emerald-400">{r.volume}</div>
            <div className="text-[10px] text-slate-400 flex justify-between pt-1 border-t border-white/[0.04]">
              <span>{r.transactions} txns</span>
              <span className="text-emerald-400 font-bold">{r.successRate}</span>
            </div>
          </div>
        ))}
      </div>
    </AGCard>
  );
}
