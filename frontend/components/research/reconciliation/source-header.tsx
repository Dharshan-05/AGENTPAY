'use client';

import { Scale, RefreshCw, FileText } from 'lucide-react';

interface SourceHeaderProps {
  onRefresh: () => void;
  onExport: () => void;
}

export function SourceHeader({ onRefresh, onExport }: SourceHeaderProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      
      {/* SOURCE ATTRIBUTION BANNER */}
      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-blue-100 text-blue-800 font-bold rounded text-[10px] uppercase">
            SOURCE EXCAVATION REFERENCE
          </span>
          <span className="font-semibold text-slate-700">Primary Repositories:</span>
          <span className="font-mono text-slate-600 text-[11px]">killbill/killbill · juspay/hyperswitch</span>
        </div>
        <span className="text-[10px] text-slate-500 font-medium">Route: /research/reconciliation-source</span>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Scale className="w-6 h-6 text-blue-600" />
            Transaction Reconciliation & Dispute Operations Source UI
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Excavated information architecture reproducing multi-gateway settlement matching, variance audit logs, and chargeback evidence state machines.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={onRefresh}
            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl border border-slate-200 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Feed
          </button>
          <button
            onClick={onExport}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            Export Audit Ledger
          </button>
        </div>
      </div>
    </div>
  );
}
