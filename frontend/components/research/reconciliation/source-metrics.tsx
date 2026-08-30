'use client';

import { Scale, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';

export function SourceMetrics() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          TOTAL SETTLED 24H
        </span>
        <div className="text-xl font-bold text-slate-900">$4,607,100.00</div>
        <span className="text-[10px] text-emerald-600 font-semibold font-sans">+99.98% Matched</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          ACTIVE DISPUTES
        </span>
        <div className="text-xl font-bold text-rose-600">3 OPEN</div>
        <span className="text-[10px] text-slate-500 font-sans">$17,100.00 Under Arbitration</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          UNRESOLVED VARIANCES
        </span>
        <div className="text-xl font-bold text-amber-600">-$12,430.00</div>
        <span className="text-[10px] text-slate-500 font-sans">2 Unmatched Gateway Clearings</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          WIN RATE (CHARGEBACKS)
        </span>
        <div className="text-xl font-bold text-blue-600">94.2%</div>
        <span className="text-[10px] text-emerald-600 font-semibold font-sans">+4.1% vs Industry Standard</span>
      </div>
    </div>
  );
}
