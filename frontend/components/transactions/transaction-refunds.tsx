'use client';

import { TxnRefund } from './transaction-types';

interface TransactionRefundsProps {
  refunds: TxnRefund[];
}

export function TransactionRefunds({ refunds }: TransactionRefundsProps) {
  const succeededCount = refunds.filter(r => r.status === 'SUCCEEDED').length;
  const processingCount = refunds.filter(r => r.status === 'PROCESSING').length;
  const failedCount = refunds.filter(r => r.status === 'FAILED').length;

  return (
    <div className="space-y-6">
      {/* SUMMARY STAT CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 font-mono">
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08]">
          <div className="text-[10px] text-slate-500 uppercase">TOTAL REFUNDS</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">{refunds.length} ISSUED</div>
          <div className="text-[10px] text-slate-400 mt-1">TOTAL AMOUNT: $7,040.00</div>
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08]">
          <div className="text-[10px] text-slate-500 uppercase">SUCCEEDED</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{succeededCount} CLEARED</div>
          <div className="text-[10px] text-emerald-400 mt-1">$4,500.00 COMPLETED</div>
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08]">
          <div className="text-[10px] text-slate-500 uppercase">PROCESSING</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">{processingCount} IN FLIGHT</div>
          <div className="text-[10px] text-blue-400 mt-1">$2,500.00 PENDING</div>
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08]">
          <div className="text-[10px] text-slate-500 uppercase">FAILED / REJECTED</div>
          <div className="text-2xl font-bold text-red-400 mt-1">{failedCount} FAILED</div>
          <div className="text-[10px] text-red-400 mt-1">POLICY EXCEPTION</div>
        </div>
      </div>

      {/* REFUNDS TABLE */}
      <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.08] bg-slate-950/60 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
                <th className="px-4 py-3 font-semibold">REFUND ID</th>
                <th className="px-4 py-3 font-semibold">TRANSACTION</th>
                <th className="px-4 py-3 font-semibold">AGENT</th>
                <th className="px-4 py-3 font-semibold">REQUESTED</th>
                <th className="px-4 py-3 font-semibold">PROCESSED</th>
                <th className="px-4 py-3 font-semibold">REASON</th>
                <th className="px-4 py-3 font-semibold">STATUS</th>
                <th className="px-4 py-3 font-semibold">PROCESSOR</th>
                <th className="px-4 py-3 font-semibold">CREATED</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] font-mono text-xs">
              {refunds.map((ref) => {
                const isSucceeded = ref.status === 'SUCCEEDED';
                const isProcessing = ref.status === 'PROCESSING';
                const isFailed = ref.status === 'FAILED';

                return (
                  <tr key={ref.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3.5 font-bold text-purple-400">
                      {ref.refundId}
                    </td>
                    <td className="px-4 py-3.5 text-blue-400">
                      {ref.transactionId}
                    </td>
                    <td className="px-4 py-3.5 text-slate-300">
                      <div>{ref.agentId}</div>
                      <div className="text-[10px] text-slate-500">{ref.agentName}</div>
                    </td>
                    <td className="px-4 py-3.5 font-bold text-slate-100">
                      {ref.requestedAmount}
                    </td>
                    <td className="px-4 py-3.5 font-bold text-emerald-400">
                      {ref.processedAmount}
                    </td>
                    <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                      {ref.reason.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                        isSucceeded ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                        isProcessing ? 'bg-blue-500/10 text-blue-400 border-blue-500/30 animate-pulse' :
                        isFailed ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {ref.status}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-300">
                      {ref.processor}
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                      {ref.createdAt}
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
