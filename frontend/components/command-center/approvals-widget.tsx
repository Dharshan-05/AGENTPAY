'use client';

import { CheckCircle2, XCircle, Clock, ShieldAlert, ArrowRight } from 'lucide-react';

export interface ApprovalItem {
  id: string;
  agentName: string;
  intent: string;
  amount: number;
  time: string;
  status: 'APPROVED' | 'BLOCKED';
  reason: string;
}

interface ApprovalsWidgetProps {
  items: ApprovalItem[];
}

export function ApprovalsWidget({ items }: ApprovalsWidgetProps) {
  const approvedItems = items.filter((i) => i.status === 'APPROVED');
  const blockedItems = items.filter((i) => i.status === 'BLOCKED');

  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl">
      <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-display font-bold text-base text-slate-100 tracking-tight">
              RECENT DECISION VERIFICATIONS
            </h3>
            <span className="text-[10px] font-mono text-slate-400">
              Side-by-Side Audit Stream: Approved vs Blocked Intents
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Approved Stream */}
        <div>
          <div className="flex items-center justify-between mb-3 text-xs font-mono text-emerald-400 font-bold uppercase pb-2 border-b border-emerald-500/20">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Recent Authorized ({approvedItems.length})
            </span>
            <span className="text-[10px] text-slate-500">AUTO PASSED</span>
          </div>

          <div className="space-y-3">
            {approvedItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900/40 border border-emerald-500/20 rounded-xl p-3.5 font-mono text-xs text-slate-300"
              >
                <div className="flex items-center justify-between mb-1 text-[10px]">
                  <span className="text-slate-200 font-bold">{item.agentName}</span>
                  <span className="text-emerald-400 font-bold">${item.amount.toLocaleString()}</span>
                </div>
                <p className="text-[11px] text-slate-400 font-sans mb-1">{item.intent}</p>
                <div className="flex items-center justify-between text-[9px] text-slate-500 pt-1 border-t border-white/[0.04]">
                  <span>{item.reason}</span>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Blocked Stream */}
        <div>
          <div className="flex items-center justify-between mb-3 text-xs font-mono text-red-400 font-bold uppercase pb-2 border-b border-red-500/20">
            <span className="flex items-center gap-1.5">
              <XCircle className="w-4 h-4" />
              Recent Blocked ({blockedItems.length})
            </span>
            <span className="text-[10px] text-slate-500">POLICY BLOCKED</span>
          </div>

          <div className="space-y-3">
            {blockedItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900/40 border border-red-500/20 rounded-xl p-3.5 font-mono text-xs text-slate-300"
              >
                <div className="flex items-center justify-between mb-1 text-[10px]">
                  <span className="text-slate-200 font-bold">{item.agentName}</span>
                  <span className="text-red-400 font-bold">${item.amount.toLocaleString()}</span>
                </div>
                <p className="text-[11px] text-slate-400 font-sans mb-1">{item.intent}</p>
                <div className="flex items-center justify-between text-[9px] text-slate-500 pt-1 border-t border-white/[0.04]">
                  <span className="text-red-400 font-bold">{item.reason}</span>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
