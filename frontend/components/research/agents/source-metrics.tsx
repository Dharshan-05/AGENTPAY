'use client';

export function SourceMetrics() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          REGISTERED AGENTS
        </span>
        <div className="text-xl font-bold text-slate-900">42 ACTIVE</div>
        <span className="text-[10px] text-emerald-600 font-semibold font-sans">100% Zero-Trust Identity Verified</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          EXECUTIONS 24H
        </span>
        <div className="text-xl font-bold text-blue-600">142,890</div>
        <span className="text-[10px] text-slate-500 font-sans">Avg Latency: 142ms</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          SUSPENDED / RISK ALERTS
        </span>
        <div className="text-xl font-bold text-amber-600">1 SUSPENDED</div>
        <span className="text-[10px] text-rose-600 font-semibold font-sans">AGT-118 Variance Policy Breach</span>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-1">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block font-sans">
          CREDENTIAL ROTATION
        </span>
        <div className="text-xl font-bold text-emerald-600">100% VALID</div>
        <span className="text-[10px] text-slate-500 font-sans">mTLS Certs & API Keys Enforced</span>
      </div>
    </div>
  );
}
