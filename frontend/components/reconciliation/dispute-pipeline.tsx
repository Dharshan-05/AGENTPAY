'use client';

import { AGCard } from '@/components/ui/ag-card';

export function DisputePipeline() {
  const steps = [
    { label: 'OPENED', count: 8, color: 'text-slate-200', bg: 'bg-slate-950/80 border-white/10' },
    { label: 'UNDER REVIEW', count: 11, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
    { label: 'EVIDENCE PREPARING', count: 9, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30' },
    { label: 'SUBMITTED', count: 6, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/30' },
    { label: 'WON', count: 84, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
    { label: 'LOST', count: 7, color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30' },
  ];

  return (
    <AGCard className="space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.08]">
        <span className="font-bold text-slate-100 text-xs">CHARGEBACK & DISPUTE LIFECYCLE PIPELINE</span>
        <span className="text-[10px] text-slate-400">Real-time arbitration dossier states</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {steps.map((s) => (
          <div key={s.label} className={`p-3 rounded-xl border ${s.bg} space-y-1 text-center`}>
            <span className="text-[9px] text-slate-400 font-bold uppercase block">{s.label}</span>
            <div className={`text-base font-bold ${s.color}`}>{s.count}</div>
          </div>
        ))}
      </div>
    </AGCard>
  );
}
