'use client';

import { Send, RefreshCw, Activity, FileText } from 'lucide-react';

interface SourceHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
}

export function SourceHeader({ onRefresh, onExport }: SourceHeaderProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      {/* SOURCE ATTRIBUTION BANNER */}
      <div className="bg-slate-50 border-b border-slate-200 px-5 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-purple-100 text-purple-800 font-bold rounded text-[10px] uppercase tracking-wide">
            PHASE 13A — SOURCE EXCAVATION REFERENCE
          </span>
          <span className="font-semibold text-slate-600">Primary Sources:</span>
          <span className="font-mono text-slate-500 text-[11px]">
            triggerdotdev/trigger.dev (96) · getlago/lago (91) · n8n-io/n8n (85) · medusajs/medusa (78) · supabase/supabase (74)
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-[10px] text-slate-500 font-medium">LIVE EVENT STREAM</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">/research/webhooks-source</span>
        </div>
      </div>

      <div className="p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 bg-purple-50 rounded-xl border border-purple-100">
            <Send className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Webhook &amp; Event Operations Control Plane
            </h1>
            <p className="text-xs text-slate-500 mt-0.5 max-w-2xl">
              Enterprise event delivery, webhook observability, payload inspection, signature security, retry schedules, and immutable event audit logs.
              Excavated from Trigger.dev, Lago, n8n, Medusa, and Supabase.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs flex-shrink-0">
          <div className="flex items-center gap-3 mr-3 text-[11px] font-mono text-slate-500">
            <span>ENDPOINTS <strong className="text-slate-800">6</strong></span>
            <span>DELIVERIES 24H <strong className="text-emerald-600">142.8k</strong></span>
            <span>SUCCESS <strong className="text-emerald-600">99.92%</strong></span>
          </div>
          <button
            onClick={onRefresh}
            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl border border-slate-200 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <button
            onClick={onExport}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <Activity className="w-3.5 h-3.5" />
            Stream Stream
          </button>
          <button
            onClick={onExport}
            className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            Export Log
          </button>
        </div>
      </div>
    </div>
  );
}
