'use client';

import { TxnPaymentIntent } from './transaction-types';

interface PaymentIntentsViewProps {
  intents: TxnPaymentIntent[];
}

export function PaymentIntentsView({ intents }: PaymentIntentsViewProps) {
  return (
    <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/60 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">INTENT ID</th>
              <th className="px-4 py-3 font-semibold">AGENT</th>
              <th className="px-4 py-3 font-semibold">MERCHANT</th>
              <th className="px-4 py-3 font-semibold">AMOUNT</th>
              <th className="px-4 py-3 font-semibold">INTENT TYPE</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">POLICY</th>
              <th className="px-4 py-3 font-semibold">RISK</th>
              <th className="px-4 py-3 font-semibold">3DS</th>
              <th className="px-4 py-3 font-semibold">UPDATED</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] font-mono text-xs">
            {intents.map((intent) => {
              const isCaptured = intent.status === 'CAPTURED' || intent.status === 'AUTHORIZED';
              const isFailed = intent.status === 'FAILED' || intent.status === 'CANCELLED';

              return (
                <tr key={intent.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-purple-400">
                    {intent.intentId}
                  </td>
                  <td className="px-4 py-3.5 text-slate-300">
                    <div>{intent.agentId}</div>
                    <div className="text-[10px] text-slate-500">{intent.agentName}</div>
                  </td>
                  <td className="px-4 py-3.5 text-slate-200 font-medium">
                    {intent.merchant}
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-100">
                    {intent.requestedAmount}
                  </td>
                  <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                    {intent.intentType.replace(/_/g, ' ')}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      isCaptured ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                      isFailed ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}>
                      {intent.status}
                    </span>
                    {intent.requiresHumanApproval && (
                      <span className="ml-1.5 px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold border border-amber-500/40">
                        HITL
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-blue-400 text-[11px]">
                    {intent.policyId}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`font-bold ${
                      intent.riskScore < 30 ? 'text-emerald-400' : intent.riskScore < 60 ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {intent.riskScore}/100
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-400 text-[10px]">
                    {intent.threeDsStatus || 'N/A'}
                  </td>
                  <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                    {intent.updatedAt}
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
