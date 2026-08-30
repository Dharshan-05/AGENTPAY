'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AnalyticsEventRecord } from './analytics-types';
import { Radio } from 'lucide-react';

interface AnalyticsEventsProps {
  events: AnalyticsEventRecord[];
}

export function AnalyticsEvents({ events }: AnalyticsEventsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span className="text-sm">LIVE ANALYTICS EVENT STREAM</span>
        </div>
        <span className="text-[10px] text-slate-500">Real-Time Socket Stream</span>
      </div>

      <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.04] space-y-2 text-[11px]">
        {events.map((evt) => (
          <div key={evt.id} className="flex justify-between items-center p-2 rounded bg-slate-900/60 border border-white/[0.04] hover:bg-slate-900 transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-emerald-400 font-bold">{evt.timestamp}</span>
              <span className="text-blue-400 font-bold">{evt.type}</span>
              <span className="text-slate-300 font-semibold">{evt.agent}</span>
            </div>

            <div className="flex items-center gap-4 text-[10px]">
              <span className="text-amber-400 font-bold">Risk: {evt.riskScore}</span>
              <span className="text-emerald-400 font-bold">{evt.status}</span>
            </div>
          </div>
        ))}
      </div>
    </AGCard>
  );
}
