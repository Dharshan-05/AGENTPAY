'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { PaymentRecord } from './types';
import { PaymentTimeline } from './payment-timeline';
import { PaymentStatusBadge } from './payment-status';
import { ShieldCheck, Copy, Check, Lock, Shield, Sparkles } from 'lucide-react';
import { useState } from 'react';

interface PaymentInspectorProps {
  payment: PaymentRecord | null;
  onClose: () => void;
  onRefund: (id: string) => void;
  onRetry: (id: string) => void;
  onBlock: (id: string) => void;
}

export function PaymentInspector({
  payment,
  onClose,
  onRefund,
  onRetry,
  onBlock,
}: PaymentInspectorProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  const copyTxnHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  if (!payment) return null;

  return (
    <AGDrawer
      isOpen={!!payment}
      onClose={onClose}
      title={`PAYMENT INSPECTOR: ${payment.id}`}
      subtitle="AUTONOMOUS TRANSACTION AUDIT & SECURITY CONTEXT"
      footer={
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-3 gap-2">
            {payment.status === 'PAID' || payment.status === 'SETTLED' || payment.status === 'AUTHORIZED' || payment.status === 'CAPTURED' ? (
              <AGButton variant="danger" size="md" onClick={() => onRefund(payment.id)}>
                REFUND
              </AGButton>
            ) : (
              <AGButton variant="primary" size="md" onClick={() => onRetry(payment.id)}>
                RETRY
              </AGButton>
            )}

            <AGButton variant="warning" size="md" onClick={() => onBlock(payment.id)}>
              BLOCK
            </AGButton>

            <AGButton variant="secondary" size="md" onClick={onClose}>
              CLOSE
            </AGButton>
          </div>

          <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-white/[0.08]">
            <span>Ledger Hash: {payment.txnHash.substring(0, 16)}...</span>
            <span>Cryptographically Verified</span>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        
        {/* VERDICT BANNER */}
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase tracking-wider">TRANSACTION VERDICT</span>
            <span className="text-base font-bold text-slate-100">{payment.status}</span>
          </div>

          <PaymentStatusBadge status={payment.status} />
        </div>

        {/* SECURITY & RISK METADATA CONTEXT */}
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-emerald-400 font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> AGENTPAY SECURITY CROSS-LINK
            </span>
            <span className="text-emerald-400 font-bold">{payment.agentGuardStatus}</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">Agent Persona</span>
              <span className="font-bold text-slate-200">{payment.agentName} ({payment.agentId})</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">Governance Policy</span>
              <span className="font-bold text-blue-400">{payment.policy}</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">FRAUDGUARD Vector</span>
              <span className="font-bold text-amber-400">Score {payment.riskScore}/100 ({payment.fraudGuardStatus})</span>
            </div>
            <div className="p-2 rounded bg-slate-950/80 border border-white/[0.04]">
              <span className="text-slate-400 block">Identity State</span>
              <span className="font-bold text-emerald-400">AUTHENTICATED</span>
            </div>
          </div>
        </div>

        {/* FINANCIAL SUMMARY */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            FINANCIAL BREAKDOWN & INSTRUMENT
          </h4>
          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Gross Amount:</span>
              <span className="text-slate-100 font-bold">{payment.amount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Processing Fee:</span>
              <span className="text-slate-400">{payment.fee}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Net Merchant Payout:</span>
              <span className="text-emerald-400 font-bold">{payment.net}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Payment Instrument:</span>
              <span className="text-slate-200 font-semibold">{payment.method}</span>
            </div>
          </div>
        </div>

        {/* CUSTOMER & MERCHANT INFO */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            CUSTOMER & MERCHANT PARTICIPANTS
          </h4>
          <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1.5 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Customer Name:</span>
              <span className="text-slate-200 font-bold">{payment.customerName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Customer Email:</span>
              <span className="text-slate-300">{payment.customerEmail}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Merchant Target:</span>
              <span className="text-slate-200">{payment.merchant}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">IP Address / Node:</span>
              <span className="text-slate-400 text-[10px]">{payment.ipAddress}</span>
            </div>
          </div>
        </div>

        {/* CONNECTED LIFECYCLE TIMELINE */}
        <PaymentTimeline
          timestamp={payment.timestamp}
          status={payment.status}
          agentGuardPolicy={payment.policy}
          fraudGuardScore={payment.riskScore}
          agentId={payment.agentId}
          agentName={payment.agentName}
        />

        {/* CRYPTOGRAPHIC TRANSACTION AUDIT HASH */}
        <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] space-y-1 text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Transaction Ledger Hash:</span>
            <button
              onClick={() => copyTxnHash(payment.txnHash)}
              className="text-blue-400 hover:text-blue-300 flex items-center gap-1 font-bold"
            >
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              {copiedHash ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className="text-emerald-400 font-mono text-[9px] break-all">{payment.txnHash}</div>
        </div>

        {/* METADATA PAYLOAD */}
        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            METADATA PAYLOAD (JSON)
          </h4>
          <pre className="p-3 rounded-xl bg-slate-950 border border-white/[0.04] text-[10px] text-emerald-400 overflow-x-auto">
            {JSON.stringify(payment.metadata, null, 2)}
          </pre>
        </div>

      </div>
    </AGDrawer>
  );
}
