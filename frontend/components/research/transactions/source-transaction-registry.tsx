'use client';

import { SourceTransactionRecord, PaymentStatus, RiskTier } from './source-types';
import { ExternalLink, AlertTriangle, Clock, CheckCircle2, XCircle, Eye, Shield, User } from 'lucide-react';

interface SourceTransactionRegistryProps {
  transactions: SourceTransactionRecord[];
  onSelectTransaction: (txn: SourceTransactionRecord) => void;
  selectedId?: string;
}

function statusBadge(status: PaymentStatus) {
  const map: Record<PaymentStatus, { bg: string; text: string; label: string }> = {
    PENDING: { bg: 'bg-slate-100', text: 'text-slate-700', label: 'PENDING' },
    AUTHORIZED: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: 'AUTHORIZED' },
    CAPTURED: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'CAPTURED' },
    SETTLED: { bg: 'bg-teal-100', text: 'text-teal-800', label: 'SETTLED' },
    FAILED: { bg: 'bg-rose-100', text: 'text-rose-800', label: 'FAILED' },
    CANCELLED: { bg: 'bg-slate-100', text: 'text-slate-600', label: 'CANCELLED' },
    REFUNDED: { bg: 'bg-amber-100', text: 'text-amber-800', label: 'REFUNDED' },
    PARTIALLY_REFUNDED: { bg: 'bg-amber-50', text: 'text-amber-700', label: 'PARTIAL REFUND' },
    DISPUTED: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'DISPUTED' },
    REQUIRES_ACTION: { bg: 'bg-violet-100', text: 'text-violet-800', label: 'REQUIRES ACTION' },
    UNDER_REVIEW: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'UNDER REVIEW' },
    BLOCKED: { bg: 'bg-red-100', text: 'text-red-800', label: 'BLOCKED' },
  };
  const s = map[status] || map.PENDING;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      {(status === 'BLOCKED' || status === 'FAILED') && <XCircle className="w-3 h-3" />}
      {(status === 'SETTLED' || status === 'CAPTURED' || status === 'AUTHORIZED') && <CheckCircle2 className="w-3 h-3" />}
      {(status === 'UNDER_REVIEW' || status === 'REQUIRES_ACTION') && <Clock className="w-3 h-3" />}
      {s.label}
    </span>
  );
}

function riskBadge(tier: RiskTier, score: number) {
  const map: Record<RiskTier, { bg: string; text: string }> = {
    LOW: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
    MEDIUM: { bg: 'bg-amber-50', text: 'text-amber-700' },
    HIGH: { bg: 'bg-rose-50', text: 'text-rose-700' },
    CRITICAL: { bg: 'bg-red-100', text: 'text-red-800' },
  };
  const s = map[tier];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      <Shield className="w-3 h-3" />
      {tier} · {score}
    </span>
  );
}

function methodLabel(m: string) {
  const map: Record<string, string> = {
    VIRTUAL_CARD: '💳 VCRD',
    CARD: '💳 CARD',
    BANK_TRANSFER: '🏦 WIRE',
    ACH: '🏦 ACH',
    UPI: '📱 UPI',
    WALLET: '👜 WLLT',
    NET_BANKING: '🏦 NETBK',
    PAY_LATER: '⏱ BNPL',
  };
  return map[m] || m;
}

export function SourceTransactionRegistry({
  transactions,
  onSelectTransaction,
  selectedId,
}: SourceTransactionRegistryProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans text-xs">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Enterprise Transaction Registry</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Multi-processor payment clearing table · {transactions.length} records shown
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
          <span>EXCAVATED FROM: Hyperswitch · Kill Bill · Medusa</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[1100px]">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 bg-slate-50 text-[10px] uppercase tracking-wide font-bold">
              <th className="px-4 py-3">TXN ID / INTENT</th>
              <th className="px-4 py-3">AGENT</th>
              <th className="px-4 py-3">MERCHANT / CUSTOMER</th>
              <th className="px-4 py-3 text-right">REQUESTED</th>
              <th className="px-4 py-3 text-right">AUTHORIZED</th>
              <th className="px-4 py-3 text-right">CAPTURED</th>
              <th className="px-4 py-3">METHOD</th>
              <th className="px-4 py-3">PROCESSOR</th>
              <th className="px-4 py-3">STATUS</th>
              <th className="px-4 py-3">RISK</th>
              <th className="px-4 py-3">POLICY</th>
              <th className="px-4 py-3">CREATED</th>
              <th className="px-4 py-3 text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {transactions.length === 0 && (
              <tr>
                <td colSpan={13} className="px-4 py-12 text-center text-slate-400 text-sm">
                  No transactions match the active filters.
                </td>
              </tr>
            )}
            {transactions.map((t) => {
              const isSelected = t.id === selectedId;
              return (
                <tr
                  key={t.id}
                  className={`hover:bg-blue-50/40 transition-colors cursor-pointer ${isSelected ? 'bg-blue-50 border-l-2 border-blue-500' : ''}`}
                  onClick={() => onSelectTransaction(t)}
                >
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-900 font-mono text-[11px]">{t.transactionId}</div>
                    <div className="text-blue-600 font-mono text-[10px] font-bold mt-0.5">{t.paymentIntentId}</div>
                    <div className="text-slate-400 text-[9px] mt-0.5">ATT: {t.attemptCount} · {t.responseCode}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center">
                        <User className="w-3 h-3 text-slate-500" />
                      </div>
                      <div>
                        <div className="font-bold text-blue-700 font-mono text-[10px]">{t.agentId}</div>
                        <div className="text-slate-500 text-[10px] max-w-[110px] truncate">{t.agentName}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-800 text-[11px] max-w-[120px] truncate">{t.merchant}</div>
                    <div className="text-slate-500 text-[10px] max-w-[120px] truncate">{t.customer}</div>
                    <div className="text-slate-400 text-[9px] mt-0.5">{t.region}</div>
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-slate-900 text-[11px]">
                    {t.requestedAmount}<br />
                    <span className="text-[9px] text-slate-400 font-normal">{t.currency}</span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-emerald-700 text-[11px]">
                    {t.authorizedAmount}
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-blue-700 text-[11px]">
                    {t.capturedAmount}
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-700 text-[10px]">{methodLabel(t.paymentMethod)}</div>
                    <div className="text-slate-400 text-[9px] max-w-[100px] truncate">{t.paymentMethodDetail}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-bold text-slate-700 text-[10px] max-w-[110px] truncate">{t.processor}</div>
                    <div className="text-slate-400 font-mono text-[9px] max-w-[110px] truncate">{t.processorReference}</div>
                  </td>
                  <td className="px-4 py-3">{statusBadge(t.status)}</td>
                  <td className="px-4 py-3">{riskBadge(t.riskTier, t.riskScore)}</td>
                  <td className="px-4 py-3">
                    <div className="font-mono text-[9px] text-slate-500">{t.policyBinding}</div>
                    <div className="text-[9px] font-bold mt-0.5">
                      <span className={t.policyDecision === 'APPROVED' ? 'text-emerald-600' : t.policyDecision === 'BLOCKED' ? 'text-red-600' : 'text-amber-600'}>
                        {t.policyDecision}
                      </span>
                    </div>
                    {t.requiresHumanApproval && (
                      <div className="text-[9px] text-orange-500 font-bold flex items-center gap-0.5 mt-0.5">
                        <AlertTriangle className="w-2.5 h-2.5" /> HITL
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono text-[9px] text-slate-500">
                    <div>{t.createdTimestamp.split(' ')[0]}</div>
                    <div>{t.createdTimestamp.split(' ')[1]}</div>
                    <div className="text-slate-400 text-[8px]">{t.environment}</div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); onSelectTransaction(t); }}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-[10px] rounded-lg transition-colors border border-blue-100"
                    >
                      <Eye className="w-3 h-3" />
                      Inspect
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 flex items-center justify-between bg-slate-50">
        <span className="text-[10px] text-slate-500 font-mono">Showing {transactions.length} of 1,847 transactions</span>
        <div className="flex items-center gap-1 text-[10px] text-slate-500">
          <span>Architecture source:</span>
          <span className="font-mono font-bold text-slate-700">Hyperswitch · Kill Bill · Medusa</span>
        </div>
      </div>
    </div>
  );
}
