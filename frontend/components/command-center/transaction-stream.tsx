'use client';

import { useState } from 'react';
import { StreamEvent } from './live-stream';
import { Terminal, CheckCircle2, AlertTriangle, XCircle, ExternalLink, Filter } from 'lucide-react';

interface TransactionStreamProps {
  events: StreamEvent[];
  onSelectEvent: (event: StreamEvent) => void;
}

export function TransactionStreamTable({ events, onSelectEvent }: TransactionStreamProps) {
  const [filter, setFilter] = useState<'ALL' | 'APPROVED' | 'DENIED' | 'PENDING'>('ALL');

  const filtered = events.filter((e) => {
    if (filter === 'APPROVED') return e.policyResult === 'APPROVED';
    if (filter === 'DENIED') return e.policyResult === 'DENIED';
    if (filter === 'PENDING') return e.policyResult === 'PENDING_APPROVAL';
    return true;
  });

  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl">
      {/* Table Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-white/[0.08] mb-6 gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-display font-bold text-base text-slate-100 tracking-tight flex items-center gap-2">
              LIVE TRANSACTION STREAM & AUDIT LEDGER
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            </h3>
            <span className="text-[10px] font-mono text-slate-400">
              Real-Time Execution & Cryptographic Verification Feed
            </span>
          </div>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-white/[0.08] rounded-lg p-1">
          <Filter className="w-3.5 h-3.5 text-slate-500 ml-1.5" />
          {(['ALL', 'APPROVED', 'DENIED', 'PENDING'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded font-mono text-[10px] uppercase transition-colors ${
                filter === f
                  ? 'bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Stream Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-white/[0.08] text-[10px] text-slate-400 uppercase">
              <th className="pb-3 px-3">Decision</th>
              <th className="pb-3 px-3">Agent Identity</th>
              <th className="pb-3 px-3">Financial Intent</th>
              <th className="pb-3 px-3 text-right">Amount ($)</th>
              <th className="pb-3 px-3 text-right">Risk Score</th>
              <th className="pb-3 px-3 text-right">Hash / Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {filtered.map((evt) => {
              const isApproved = evt.policyResult === 'APPROVED';
              const isDenied = evt.policyResult === 'DENIED';

              return (
                <tr
                  key={evt.id}
                  onClick={() => onSelectEvent(evt)}
                  className="hover:bg-slate-900/60 transition-colors cursor-pointer group"
                >
                  {/* Decision State Badge */}
                  <td className="py-3.5 px-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] uppercase font-bold ${
                        isApproved
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : isDenied
                          ? 'bg-red-500/10 text-red-400 border-red-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {isApproved ? (
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      ) : isDenied ? (
                        <XCircle className="w-3 h-3 text-red-400" />
                      ) : (
                        <AlertTriangle className="w-3 h-3 text-amber-400" />
                      )}
                      {isApproved ? 'AUTHORIZED' : isDenied ? 'BLOCKED' : 'REVIEW'}
                    </span>
                  </td>

                  {/* Agent Name */}
                  <td className="py-3.5 px-3 text-slate-100 font-bold">
                    {evt.agentName}
                  </td>

                  {/* Intent Payload */}
                  <td className="py-3.5 px-3 text-slate-300 font-sans max-w-xs truncate">
                    {evt.intent}
                  </td>

                  {/* Amount */}
                  <td className="py-3.5 px-3 text-right text-slate-100 font-bold">
                    ${evt.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>

                  {/* Risk Score */}
                  <td className="py-3.5 px-3 text-right">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.riskScore > 0.4 ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400'
                      }`}
                    >
                      {evt.riskScore.toFixed(2)} ({evt.riskScore > 0.4 ? 'HIGH' : 'LOW'})
                    </span>
                  </td>

                  {/* Hash / Time */}
                  <td className="py-3.5 px-3 text-right text-slate-500 text-[10px]">
                    <div className="flex items-center justify-end gap-1">
                      <span>{evt.timestamp}</span>
                      <ExternalLink className="w-3 h-3 text-slate-600 group-hover:text-slate-300 transition-colors" />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
