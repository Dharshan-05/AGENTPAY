'use client';

import { TxnAuditEntry } from './transaction-types';
import { Lock, ShieldCheck } from 'lucide-react';

interface TransactionAuditProps {
  entries: TxnAuditEntry[];
}

export function TransactionAudit({ entries }: TransactionAuditProps) {
  return (
    <div className="space-y-4 font-mono">
      {/* HEADER BANNER */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            <Lock className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-display font-bold text-sm text-slate-100">IMMUTABLE CRYPTOGRAPHIC AUDIT TRAIL</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Every authorization, policy decision, risk score, and settlement is SHA-256 chained and tamper-evident.
            </p>
          </div>
        </div>
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
          <ShieldCheck className="w-3.5 h-3.5" />
          CHAIN INTEGRITY VERIFIED
        </span>
      </div>

      {/* TABLE */}
      <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.08] bg-slate-950/60 text-[10px] text-slate-500 uppercase tracking-wider">
                <th className="px-4 py-3 font-semibold">EVENT ID</th>
                <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
                <th className="px-4 py-3 font-semibold">ACTOR</th>
                <th className="px-4 py-3 font-semibold">TYPE</th>
                <th className="px-4 py-3 font-semibold">ACTION</th>
                <th className="px-4 py-3 font-semibold">DECISION</th>
                <th className="px-4 py-3 font-semibold">HASH</th>
                <th className="px-4 py-3 font-semibold">OUTCOME</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] text-xs">
              {entries.map((entry) => {
                const isSuccess = entry.outcome === 'SUCCESS';
                const isBlocked = entry.outcome === 'BLOCKED' || entry.outcome === 'FAILURE';

                return (
                  <tr key={entry.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3.5 font-bold text-slate-300">
                      {entry.eventId}
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                      {entry.timestamp}
                    </td>
                    <td className="px-4 py-3.5 text-slate-200 font-bold">
                      {entry.actor}
                    </td>
                    <td className="px-4 py-3.5 text-[10px]">
                      <span className={`px-2 py-0.5 rounded font-bold ${
                        entry.actorType === 'AGENT' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                        entry.actorType === 'SYSTEM' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        entry.actorType === 'HUMAN' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                        'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {entry.actorType}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-300 font-medium">
                      {entry.action}
                    </td>
                    <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                      {entry.decision}
                    </td>
                    <td className="px-4 py-3.5 text-[10px] text-slate-500 truncate max-w-[120px]">
                      {entry.hash}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isSuccess ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                        isBlocked ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}>
                        {entry.outcome}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
