'use client';

import { AGCard } from '@/components/ui/ag-card';
import { Activity } from 'lucide-react';
import { useState } from 'react';

export function TransactionTelemetry() {
  const [range, setRange] = useState<'1H' | '24H' | '7D' | '30D'>('24H');

  return (
    <AGCard className="space-y-4">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] font-mono text-xs gap-3">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>TRANSACTION INTELLIGENCE TELEMETRY</span>
        </div>

        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-[10px]">
          {(['1H', '24H', '7D', '30D'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                range === r
                  ? 'bg-emerald-500 text-slate-950 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="text-[10px] text-slate-400 font-mono">
        Aggregated payment execution, agent activity, authorization and risk behavior.
      </div>

      {/* Chart SVG Surface */}
      <div className="h-64 rounded-xl bg-slate-950/90 border border-white/[0.04] p-4 flex flex-col justify-between font-mono text-xs relative overflow-hidden">
        <div className="flex justify-between items-center text-[10px] text-slate-500">
          <span>Transaction Volume Overlay: Successful (Emerald) · Pending (Amber) · Failed (Red)</span>
          <span>Live Stream Data</span>
        </div>

        <div className="h-44 w-full flex items-end justify-between gap-3 pt-4">
          {[
            { succ: 65, pend: 15, fail: 5 },
            { succ: 78, pend: 18, fail: 4 },
            { succ: 85, pend: 12, fail: 6 },
            { succ: 92, pend: 20, fail: 8 },
            { succ: 96, pend: 14, fail: 3 },
            { succ: 70, pend: 10, fail: 5 },
            { succ: 88, pend: 16, fail: 4 },
            { succ: 94, pend: 22, fail: 9 },
            { succ: 82, pend: 18, fail: 6 },
            { succ: 90, pend: 15, fail: 5 },
          ].map((d, idx) => (
            <div key={idx} className="flex-1 flex items-end justify-center gap-1 h-full">
              <div
                className="w-1/3 bg-emerald-500/80 rounded-t hover:bg-emerald-400 transition-colors"
                style={{ height: `${d.succ}%` }}
                title={`Successful: ${d.succ}%`}
              />
              <div
                className="w-1/3 bg-amber-500/80 rounded-t hover:bg-amber-400 transition-colors"
                style={{ height: `${d.pend}%` }}
                title={`Pending: ${d.pend}%`}
              />
              <div
                className="w-1/3 bg-red-500/80 rounded-t hover:bg-red-400 transition-colors"
                style={{ height: `${d.fail}%` }}
                title={`Failed: ${d.fail}%`}
              />
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between text-[10px] pt-2 border-t border-white/[0.06] text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-emerald-400" /> Successful</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-amber-400" /> Pending</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded bg-red-400" /> Failed / Blocked</span>
          </div>
          <span>Peak Velocity: 4,820 TPS</span>
        </div>
      </div>
    </AGCard>
  );
}
