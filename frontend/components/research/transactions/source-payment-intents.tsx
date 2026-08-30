'use client';

import { SourcePaymentIntent, PaymentIntentStatus } from './source-types';
import { Clock, CheckCircle2, XCircle, AlertTriangle, User, Eye } from 'lucide-react';

interface SourcePaymentIntentsProps {
  intents: SourcePaymentIntent[];
  onSelectIntent?: (pi: SourcePaymentIntent) => void;
}

function intentStatusBadge(status: PaymentIntentStatus) {
  const map: Record<PaymentIntentStatus, { bg: string; text: string; icon: React.ReactNode }> = {
    CREATED: { bg: 'bg-slate-100', text: 'text-slate-700', icon: <Clock className="w-3 h-3" /> },
    REQUIRES_AUTHORIZATION: { bg: 'bg-violet-100', text: 'text-violet-800', icon: <AlertTriangle className="w-3 h-3" /> },
    REQUIRES_ACTION: { bg: 'bg-orange-100', text: 'text-orange-800', icon: <AlertTriangle className="w-3 h-3" /> },
    AUTHORIZED: { bg: 'bg-emerald-100', text: 'text-emerald-800', icon: <CheckCircle2 className="w-3 h-3" /> },
    CAPTURED: { bg: 'bg-blue-100', text: 'text-blue-800', icon: <CheckCircle2 className="w-3 h-3" /> },
    PARTIALLY_CAPTURED: { bg: 'bg-blue-50', text: 'text-blue-700', icon: <CheckCircle2 className="w-3 h-3" /> },
    FAILED: { bg: 'bg-rose-100', text: 'text-rose-800', icon: <XCircle className="w-3 h-3" /> },
    CANCELLED: { bg: 'bg-slate-100', text: 'text-slate-600', icon: <XCircle className="w-3 h-3" /> },
    REFUNDED: { bg: 'bg-amber-100', text: 'text-amber-800', icon: <AlertTriangle className="w-3 h-3" /> },
    PARTIALLY_REFUNDED: { bg: 'bg-amber-50', text: 'text-amber-700', icon: <AlertTriangle className="w-3 h-3" /> },
    DISPUTED: { bg: 'bg-red-100', text: 'text-red-800', icon: <XCircle className="w-3 h-3" /> },
  };
  const s = map[status];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      {s.icon}
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function approvalBadge(status?: string) {
  if (!status) return null;
  const map: Record<string, { bg: string; text: string }> = {
    PENDING: { bg: 'bg-orange-100', text: 'text-orange-800' },
    APPROVED: { bg: 'bg-emerald-100', text: 'text-emerald-800' },
    REJECTED: { bg: 'bg-rose-100', text: 'text-rose-800' },
  };
  const s = map[status] || map.PENDING;
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.bg} ${s.text}`}>
      HITL: {status}
    </span>
  );
}

export function SourcePaymentIntents({ intents, onSelectIntent }: SourcePaymentIntentsProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans text-xs">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Payment Intent Pipeline</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Agent-originated payment intent lifecycle tracking · {intents.length} active intents
          </p>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">SOURCE: juspay/hyperswitch · Stripe Payment Intents</div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[1200px]">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 bg-slate-50 text-[10px] uppercase tracking-wide font-bold">
              <th className="px-4 py-3">INTENT ID / TXN</th>
              <th className="px-4 py-3">AGENT</th>
              <th className="px-4 py-3">INTENT TYPE</th>
              <th className="px-4 py-3">MERCHANT / CUSTOMER</th>
              <th className="px-4 py-3 text-right">REQUESTED</th>
              <th className="px-4 py-3 text-right">AUTHORIZED</th>
              <th className="px-4 py-3 text-right">CAPTURED</th>
              <th className="px-4 py-3">POLICY / RISK</th>
              <th className="px-4 py-3">PROCESSOR</th>
              <th className="px-4 py-3">3DS</th>
              <th className="px-4 py-3">STATUS</th>
              <th className="px-4 py-3">APPROVAL</th>
              <th className="px-4 py-3">EXPIRES</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {intents.map((pi) => (
              <tr
                key={pi.id}
                className="hover:bg-blue-50/30 transition-colors cursor-pointer"
                onClick={() => onSelectIntent && onSelectIntent(pi)}
              >
                <td className="px-4 py-3">
                  <div className="font-bold text-blue-700 font-mono text-[11px]">{pi.intentId}</div>
                  <div className="text-slate-500 font-mono text-[10px]">{pi.transactionId}</div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-5 h-5 rounded-full bg-blue-50 flex items-center justify-center">
                      <User className="w-3 h-3 text-blue-500" />
                    </div>
                    <div>
                      <div className="font-bold text-blue-700 font-mono text-[10px]">{pi.agentId}</div>
                      <div className="text-slate-500 text-[10px] max-w-[100px] truncate">{pi.agentName}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="bg-slate-100 text-slate-700 text-[9px] font-bold px-2 py-1 rounded font-mono max-w-[140px]">
                    {pi.intentType.replace(/_/g, ' ')}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="font-bold text-slate-800 text-[11px] max-w-[110px] truncate">{pi.merchant}</div>
                  <div className="text-slate-500 text-[10px] max-w-[110px] truncate">{pi.customer}</div>
                </td>
                <td className="px-4 py-3 text-right font-mono font-bold text-slate-900 text-[11px]">
                  {pi.requestedAmount}<br />
                  <span className="text-[9px] text-slate-400 font-normal">{pi.currency}</span>
                </td>
                <td className="px-4 py-3 text-right font-mono font-bold text-emerald-700 text-[11px]">
                  {pi.authorizedAmount}
                </td>
                <td className="px-4 py-3 text-right font-mono font-bold text-blue-700 text-[11px]">
                  {pi.capturedAmount}
                </td>
                <td className="px-4 py-3">
                  <div className="font-mono text-[9px] text-slate-500">{pi.policyId}</div>
                  <div className={`text-[9px] font-bold mt-0.5 ${pi.riskTier === 'HIGH' || pi.riskTier === 'CRITICAL' ? 'text-rose-600' : pi.riskTier === 'MEDIUM' ? 'text-amber-600' : 'text-emerald-600'}`}>
                    RISK: {pi.riskTier} · {pi.riskScore}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-slate-700 text-[10px] font-bold max-w-[90px] truncate">{pi.processor}</div>
                  <div className="text-slate-500 text-[10px]">{pi.paymentMethod.replace(/_/g, ' ')}</div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    pi.threeDsStatus === 'AUTHENTICATED' ? 'bg-emerald-100 text-emerald-700' :
                    pi.threeDsStatus === 'FAILED' ? 'bg-rose-100 text-rose-700' :
                    'bg-slate-100 text-slate-500'
                  }`}>
                    {pi.threeDsStatus || 'N/A'}
                  </span>
                </td>
                <td className="px-4 py-3">{intentStatusBadge(pi.status)}</td>
                <td className="px-4 py-3">
                  {pi.requiresHumanApproval ? approvalBadge(pi.humanApprovalStatus) : (
                    <span className="text-[10px] text-slate-400">AUTO</span>
                  )}
                </td>
                <td className="px-4 py-3 font-mono text-[9px] text-slate-500">
                  {pi.expirationTime.split(' ')[1]}<br/>
                  <span className="text-[8px]">{pi.expirationTime.split(' ')[0]}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
        <span className="text-[10px] text-slate-500 font-mono">
          States: CREATED → REQUIRES_AUTHORIZATION → AUTHORIZED → CAPTURED → SETTLED / FAILED / REFUNDED / DISPUTED
        </span>
        <span className="text-[10px] text-slate-400 font-mono">PATTERN: Stripe PaymentIntents · Hyperswitch</span>
      </div>
    </div>
  );
}
