'use client';

import { Layers, ShieldCheck, CheckCircle2, AlertTriangle } from 'lucide-react';

interface PaymentTimelineProps {
  timestamp: string;
  status: string;
  agentGuardPolicy: string;
  fraudGuardScore: number;
  agentId: string;
  agentName: string;
}

export function PaymentTimeline({
  timestamp,
  status,
  agentGuardPolicy,
  fraudGuardScore,
  agentId,
  agentName,
}: PaymentTimelineProps) {
  return (
    <div className="space-y-2">
      <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5 font-mono">
        <Layers className="w-3.5 h-3.5 text-emerald-400" />
        CONNECTED PAYMENT SECURITY LIFECYCLE TIMELINE
      </h4>

      <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-3 font-mono text-[10px]">
        
        {/* Step 1 */}
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px] shrink-0">
            01
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-bold text-slate-200">Agent Intent Received & Authenticated</span>
              <span className="text-slate-500">{timestamp}</span>
            </div>
            <p className="text-slate-400 text-[9px]">
              {agentName} ({agentId}) initiated spending transaction payload via mTLS authenticated session.
            </p>
          </div>
        </div>

        {/* Step 2 */}
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-[9px] shrink-0">
            02
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-bold text-blue-400">AGENTGUARD Policy Evaluation</span>
              <span className="text-slate-400 font-bold">{agentGuardPolicy}</span>
            </div>
            <p className="text-slate-400 text-[9px]">
              Zero-Trust spending limit and MCC permission rules evaluated cleanly. Result: PASSED.
            </p>
          </div>
        </div>

        {/* Step 3 */}
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 flex items-center justify-center font-bold text-[9px] shrink-0">
            03
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-bold text-purple-400">FRAUDGUARD Risk Vector Scoring</span>
              <span className="text-slate-400 font-bold">Score: {fraudGuardScore}/100</span>
            </div>
            <p className="text-slate-400 text-[9px]">
              Synthetic identity and device collision models executed. Risk band: {fraudGuardScore < 30 ? 'LOW RISK' : 'ELEVATED'}.
            </p>
          </div>
        </div>

        {/* Step 4 */}
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[9px] shrink-0">
            04
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-bold text-emerald-400">Payment Authorization & Capture</span>
              <span className="text-emerald-400 font-bold">{status}</span>
            </div>
            <p className="text-slate-400 text-[9px]">
              Transaction routed to Visa/Mastercard processing network. Network Auth Response: 00 (Approved).
            </p>
          </div>
        </div>

        {/* Step 5 */}
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-[9px] shrink-0">
            05
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-bold text-slate-300">Settlement & Payout Queue</span>
              <span className="text-slate-400">T+1 Batch #po_8812A</span>
            </div>
            <p className="text-slate-400 text-[9px]">
              Merchant net funds committed for daily wire transfer settlement to destination bank.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
