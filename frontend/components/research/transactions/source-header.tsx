'use client';

import { CreditCard, RefreshCw, FileText, Activity } from 'lucide-react';

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
          <span className="px-2 py-0.5 bg-blue-100 text-blue-800 font-bold rounded text-[10px] uppercase tracking-wide">
            PHASE 12A — SOURCE EXCAVATION REFERENCE
          </span>
          <span className="font-semibold text-slate-600">Primary Sources:</span>
          <span className="font-mono text-slate-500 text-[11px]">
            juspay/hyperswitch · killbill/killbill · getlago/lago · medusajs/medusa · apache/fineract
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-[10px] text-slate-500 font-medium">LIVE FEED</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">/research/transactions-source</span>
        </div>
      </div>

      <div className="p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 bg-blue-50 rounded-xl border border-blue-100">
            <CreditCard className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Payment Intent &amp; Transaction Operations Control Plane
            </h1>
            <p className="text-xs text-slate-500 mt-0.5 max-w-2xl">
              Enterprise-grade transaction operations console. Excavated architecture from Hyperswitch, Kill Bill, Lago, Medusa, and Apache Fineract.
              Full lifecycle coverage: intent → identity → policy → risk → authorization → capture → settlement → audit.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs flex-shrink-0">
          <div className="flex items-center gap-3 mr-3 text-[11px] font-mono text-slate-500">
            <span>TRANSACTIONS <strong className="text-slate-800">1,847</strong></span>
            <span>INTENTS <strong className="text-blue-600">1,420</strong></span>
            <span>BLOCKED <strong className="text-rose-600">3</strong></span>
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
            Stream Feed
          </button>
          <button
            onClick={onExport}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            Export Ledger
          </button>
        </div>
      </div>
    </div>
  );
}
