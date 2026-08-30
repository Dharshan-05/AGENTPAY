'use client';

import { BarChart3, RefreshCw, Download, FileText, Calendar, Filter } from 'lucide-react';

interface SourceHeaderProps {
  dateRange: string;
  onDateRangeChange: (r: string) => void;
  onRefresh: () => void;
  onExport: () => void;
}

export function SourceHeader({ dateRange, onDateRangeChange, onRefresh, onExport }: SourceHeaderProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      
      {/* SOURCE REPOSITORY ATTRIBUTION BANNER */}
      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-blue-100 text-blue-800 font-bold rounded text-[10px] uppercase">
            SOURCE EXCAVATION REFERENCE
          </span>
          <span className="font-semibold text-slate-700">Repositories:</span>
          <span className="font-mono text-slate-600 text-[11px]">tremorlabs/tremor · shadcn-ui/analytics-dashboard</span>
        </div>
        <span className="text-[10px] text-slate-500 font-medium">Route: /research/analytics-source</span>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            Financial Intelligence & Analytics Source UI
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Excavated source layout reproducing executive KPIs, transaction charts, risk vectors, agent matrices, and anomaly streams.
          </p>
        </div>

        {/* CONTROLS */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <Calendar className="w-3.5 h-3.5 text-slate-500 ml-1.5" />
            {['24H', '7D', '30D', '90D', 'CUSTOM'].map((r) => (
              <button
                key={r}
                onClick={() => onDateRangeChange(r)}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  dateRange === r
                    ? 'bg-white text-blue-700 shadow-sm font-bold border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          <button
            onClick={onRefresh}
            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl border border-slate-200 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>

          <button
            onClick={onExport}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
}
