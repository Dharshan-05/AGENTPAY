'use client';

import { TrendingUp, ShieldAlert, Layers } from 'lucide-react';

export function SourceCharts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-sans text-slate-800">
      
      {/* Transaction Volume Chart */}
      <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              Transaction Velocity & Authorization Volume
            </h3>
            <p className="text-xs text-slate-500">Excavated time-series visualization pattern (Tremor chart styling)</p>
          </div>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
            24-Hour Real-Time
          </span>
        </div>

        {/* SVG Chart Visualization */}
        <div className="h-56 w-full bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between font-mono text-xs">
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Volume ($)</span>
            <span>Peak: $420,000 / hr</span>
          </div>

          <div className="h-36 w-full flex items-end justify-between gap-2 pt-2">
            {[42, 58, 64, 78, 92, 85, 60, 74, 88, 95, 100, 82].map((v, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                <div
                  className="w-full bg-blue-600 rounded-t hover:bg-blue-700 transition-colors"
                  style={{ height: `${v}%` }}
                />
              </div>
            ))}
          </div>

          <div className="flex justify-between text-[10px] text-slate-500 pt-2 border-t border-slate-200">
            <span>00:00 UTC</span>
            <span>06:00 UTC</span>
            <span>12:00 UTC</span>
            <span>18:00 UTC</span>
            <span>24:00 UTC</span>
          </div>
        </div>
      </div>

      {/* Risk Distribution Matrix */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-100">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            Risk Vector Distribution
          </h3>
          <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
            Avg 56.4
          </span>
        </div>

        <div className="space-y-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
            <span className="text-slate-600 font-medium">Low Risk (0-39)</span>
            <span className="font-bold text-emerald-700 font-mono">1,422 (82%)</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
            <span className="text-slate-600 font-medium">Medium Risk (40-74)</span>
            <span className="font-bold text-amber-700 font-mono">48 (14%)</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
            <span className="text-slate-600 font-medium">High / Critical (75-100)</span>
            <span className="font-bold text-rose-700 font-mono">12 (4%)</span>
          </div>

          <div className="pt-2">
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex">
              <div className="bg-emerald-500 h-full" style={{ width: '82%' }} />
              <div className="bg-amber-500 h-full" style={{ width: '14%' }} />
              <div className="bg-rose-500 h-full" style={{ width: '4%' }} />
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
