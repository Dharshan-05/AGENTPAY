'use client';

import { SourceRefundRecord, RefundStatus } from './source-types';
import { CheckCircle2, Loader2, XCircle, Clock } from 'lucide-react';

interface SourceRefundsProps {
  refunds: SourceRefundRecord[];
}

function refundStatusBadge(status: RefundStatus) {
  const map: Record<RefundStatus, { bg: string; text: string; icon: React.ReactNode }> = {
    REQUESTED: { bg: 'bg-slate-100', text: 'text-slate-700', icon: <Clock className="w-3 h-3" /> },
    PROCESSING: { bg: 'bg-blue-100', text: 'text-blue-800', icon: <Loader2 className="w-3 h-3 animate-spin" /> },
    COMPLETED: { bg: 'bg-emerald-100', text: 'text-emerald-800', icon: <CheckCircle2 className="w-3 h-3" /> },
    FAILED: { bg: 'bg-rose-100', text: 'text-rose-800', icon: <XCircle className="w-3 h-3" /> },
    PARTIAL: { bg: 'bg-amber-100', text: 'text-amber-800', icon: <Clock className="w-3 h-3" /> },
  };
  const s = map[status];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      {s.icon}
      {status}
    </span>
  );
}

function reasonLabel(r: string) {
  const map: Record<string, string> = {
    DUPLICATE_CHARGE: '🔁 Duplicate Charge',
    POLICY_VIOLATION: '🛡 Policy Violation',
    CANCELLED_SERVICE: '❌ Cancelled Service',
    AGENT_UNAUTHORIZED: '⚠️ Agent Unauthorized',
    CUSTOMER_REQUEST: '👤 Customer Request',
    FRAUD: '🚨 Fraud',
  };
  return map[r] || r;
}

export function SourceRefunds({ refunds }: SourceRefundsProps) {
  const totalRequested = refunds.reduce((acc, r) => {
    const n = parseFloat(r.requestedAmount.replace(/[$,]/g, ''));
    return acc + (isNaN(n) ? 0 : n);
  }, 0);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans text-xs">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Refunds &amp; Clearing Log</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            {refunds.length} refund records · Total: ${totalRequested.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">SOURCE: Kill Bill · Hyperswitch · Medusa</div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-slate-50 border-b border-slate-100">
        <div className="bg-white rounded-xl border border-slate-200 p-3">
          <div className="text-[9px] text-slate-400 uppercase font-bold">COMPLETED</div>
          <div className="text-base font-bold text-emerald-600 mt-1">
            {refunds.filter(r => r.status === 'COMPLETED').length}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-3">
          <div className="text-[9px] text-slate-400 uppercase font-bold">PROCESSING</div>
          <div className="text-base font-bold text-blue-600 mt-1">
            {refunds.filter(r => r.status === 'PROCESSING').length}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-3">
          <div className="text-[9px] text-slate-400 uppercase font-bold">FAILED</div>
          <div className="text-base font-bold text-rose-600 mt-1">
            {refunds.filter(r => r.status === 'FAILED').length}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 bg-slate-50 text-[10px] uppercase tracking-wide font-bold">
              <th className="px-4 py-3">REFUND ID</th>
              <th className="px-4 py-3">ORIGINAL TXN</th>
              <th className="px-4 py-3">AGENT</th>
              <th className="px-4 py-3 text-right">REQUESTED</th>
              <th className="px-4 py-3 text-right">PROCESSED</th>
              <th className="px-4 py-3">REASON</th>
              <th className="px-4 py-3">PROCESSOR REF</th>
              <th className="px-4 py-3">REQUESTED BY</th>
              <th className="px-4 py-3">STATUS</th>
              <th className="px-4 py-3">TIMESTAMPS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {refunds.map((r) => (
              <tr key={r.id} className="hover:bg-amber-50/30 transition-colors">
                <td className="px-4 py-3 font-bold font-mono text-[11px] text-slate-900">{r.refundId}</td>
                <td className="px-4 py-3 font-bold text-blue-700 font-mono text-[11px]">{r.originalTransactionId}</td>
                <td className="px-4 py-3">
                  <div className="font-bold text-blue-700 font-mono text-[10px]">{r.agentId}</div>
                  <div className="text-slate-500 text-[10px] max-w-[100px] truncate">{r.agentName}</div>
                </td>
                <td className="px-4 py-3 text-right font-mono font-bold text-slate-900 text-[11px]">
                  {r.requestedAmount} {r.currency}
                </td>
                <td className="px-4 py-3 text-right font-mono font-bold text-emerald-700 text-[11px]">
                  {r.processedAmount}
                </td>
                <td className="px-4 py-3">
                  <div className="text-[10px] font-bold text-slate-700">{reasonLabel(r.reason)}</div>
                  <div className="text-[9px] text-slate-500 max-w-[140px] truncate">{r.reasonDetail}</div>
                </td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-500 max-w-[110px] truncate">
                  {r.processorReference}
                </td>
                <td className="px-4 py-3 text-[10px] text-slate-600 font-semibold">
                  {r.requestedBy.replace(/_/g, ' ')}
                </td>
                <td className="px-4 py-3">{refundStatusBadge(r.status)}</td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-500">
                  <div>REQ: {r.requestedTimestamp.split(' ')[1]}</div>
                  {r.completedTimestamp && (
                    <div className="text-emerald-600">DONE: {r.completedTimestamp.split(' ')[1]}</div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-[10px] text-slate-400 font-mono">
        Refund States: REQUESTED → PROCESSING → COMPLETED / FAILED · Safeguards: Duplicate check, Agent authorization, Policy validation
      </div>
    </div>
  );
}
