'use client';

import { SourceKpiMetric } from './source-types';
import { ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

interface SourceMetricsProps {
  metrics: SourceKpiMetric[];
}

export function SourceMetrics({ metrics }: SourceMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-sans text-slate-800">
      {metrics.map((m, idx) => (
        <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-center text-xs font-semibold text-slate-500 uppercase tracking-wide">
            <span>{m.title}</span>
            <Activity className="w-4 h-4 text-slate-400" />
          </div>

          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 font-mono">{m.value}</span>
            <span
              className={`inline-flex items-center text-xs font-bold px-2 py-0.5 rounded-full ${
                m.isPositive
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border border-amber-200'
              }`}
            >
              {m.isPositive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
              {m.change}
            </span>
          </div>

          <p className="text-xs text-slate-500">{m.subtext}</p>
        </div>
      ))}
    </div>
  );
}
