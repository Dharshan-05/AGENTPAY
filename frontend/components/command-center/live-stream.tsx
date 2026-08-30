'use client';

import { useState } from 'react';
import { Terminal, ShieldCheck, AlertTriangle, CheckCircle2, Lock, ArrowRight, Activity } from 'lucide-react';

export interface StreamEvent {
  id: string;
  timestamp: string;
  agentId: string;
  agentName: string;
  intent: string;
  amount: number;
  policyResult: 'APPROVED' | 'DENIED' | 'PENDING_APPROVAL';
  riskScore: number;
  hash: string;
}

interface LiveStreamProps {
  events: StreamEvent[];
}

export function LiveStream({ events }: LiveStreamProps) {
  const [filter, setFilter] = useState<'ALL' | 'APPROVED' | 'DENIED' | 'PENDING'>('ALL');

  const filteredEvents = events.filter((e) => {
    if (filter === 'APPROVED') return e.policyResult === 'APPROVED';
    if (filter === 'DENIED') return e.policyResult === 'DENIED';
    if (filter === 'PENDING') return e.policyResult === 'PENDING_APPROVAL';
    return true;
  });

  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl h-full flex flex-col justify-between">
      
      {/* Header & Filter Controls */}
      <div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-white/[0.08] mb-4 gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base text-slate-100 tracking-tight flex items-center gap-2">
                LIVE TRANSACTION STREAM
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                Real-Time Execution & Policy Governance Event Bus
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 border border-white/10 rounded-lg p-1">
            {(['ALL', 'APPROVED', 'DENIED', 'PENDING'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2.5 py-1 rounded font-mono text-[10px] uppercase transition-colors ${
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

        {/* Live Stream Event List */}
        <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
          {filteredEvents.map((evt) => {
            const isApproved = evt.policyResult === 'APPROVED';
            const isDenied = evt.policyResult === 'DENIED';

            return (
              <div
                key={evt.id}
                className="bg-slate-900/60 border border-white/[0.06] hover:border-white/20 rounded-xl p-3.5 font-mono text-xs text-slate-300 transition-all"
              >
                <div className="flex items-center justify-between mb-1.5 text-[10px]">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Activity className="w-3 h-3 text-emerald-400" />
                    {evt.timestamp}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full border uppercase text-[9px] font-bold ${
                      isApproved
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : isDenied
                        ? 'bg-red-500/10 text-red-400 border-red-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    {evt.policyResult}
                  </span>
                </div>

                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-100 font-bold text-sm">
                    {evt.agentName}
                  </span>
                  <span className="text-slate-100 font-bold text-sm">
                    ${evt.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>

                <p className="text-[11px] text-slate-400 font-sans mb-2 leading-snug">
                  {evt.intent}
                </p>

                <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between text-[10px] text-slate-500">
                  <span>Risk Score: <strong className={evt.riskScore > 0.4 ? 'text-amber-400' : 'text-emerald-400'}>{evt.riskScore.toFixed(2)}</strong></span>
                  <span className="truncate max-w-[140px]" title={evt.hash}>Hash: {evt.hash}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stream Footer Metadata */}
      <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-500">
        <span>POLLING LATENCY: 12ms</span>
        <span className="text-emerald-400">SSE STREAM CONNECTED</span>
      </div>

    </div>
  );
}
