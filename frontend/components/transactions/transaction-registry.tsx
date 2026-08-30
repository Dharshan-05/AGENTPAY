'use client';

import { TxnRecord } from './transaction-types';

interface TransactionRegistryProps {
  transactions: TxnRecord[];
  onSelect: (t: TxnRecord) => void;
}

export function TransactionRegistry({ transactions, onSelect }: TransactionRegistryProps) {
  return (
    <div className="rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl overflow-hidden">
      <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-slate-950">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/60 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">TRANSACTION ID</th>
              <th className="px-4 py-3 font-semibold">PAYMENT INTENT</th>
              <th className="px-4 py-3 font-semibold">AGENT</th>
              <th className="px-4 py-3 font-semibold">MERCHANT</th>
              <th className="px-4 py-3 font-semibold">AMOUNT</th>
              <th className="px-4 py-3 font-semibold">STATUS</th>
              <th className="px-4 py-3 font-semibold">RISK</th>
              <th className="px-4 py-3 font-semibold">PROCESSOR</th>
              <th className="px-4 py-3 font-semibold">METHOD</th>
              <th className="px-4 py-3 font-semibold">ENV</th>
              <th className="px-4 py-3 font-semibold">UPDATED</th>
              <th className="px-4 py-3 font-semibold text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] font-mono text-xs">
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={12} className="px-4 py-8 text-center text-slate-500 font-mono text-xs">
                  No transactions match the selected filters.
                </td>
              </tr>
            ) : (
              transactions.map((txn) => {
                const isBlocked = txn.status === 'BLOCKED' || txn.status === 'FAILED';
                const isSuccess = txn.status === 'SETTLED' || txn.status === 'CAPTURED' || txn.status === 'AUTHORIZED';
                const isRefunded = txn.status === 'REFUNDED' || txn.status === 'PARTIALLY_REFUNDED';

                return (
                  <tr
                    key={txn.id}
                    onClick={() => onSelect(txn)}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                  >
                    <td className="px-4 py-3.5 font-bold text-blue-400 group-hover:text-blue-300">
                      {txn.transactionId}
                    </td>
                    <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                      {txn.paymentIntentId}
                    </td>
                    <td className="px-4 py-3.5 text-slate-300 font-medium">
                      <div>{txn.agentId}</div>
                      <div className="text-[10px] text-slate-500 font-normal">{txn.agentName}</div>
                    </td>
                    <td className="px-4 py-3.5 text-slate-200 truncate max-w-[160px]">
                      {txn.merchant}
                    </td>
                    <td className="px-4 py-3.5 font-bold text-slate-100">
                      {txn.requestedAmount}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                        isSuccess ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                        isBlocked ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        isRefunded ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' :
                        'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          isSuccess ? 'bg-emerald-400' : isBlocked ? 'bg-red-400' : isRefunded ? 'bg-purple-400' : 'bg-amber-400'
                        }`} />
                        {txn.status}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`font-bold ${
                        txn.riskScore < 30 ? 'text-emerald-400' : txn.riskScore < 60 ? 'text-amber-400' : 'text-red-400'
                      }`}>
                        {txn.riskScore}/100
                      </span>
                      <span className="text-[9px] text-slate-500 block uppercase">{txn.riskTier}</span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-300">
                      {txn.processor}
                    </td>
                    <td className="px-4 py-3.5 text-slate-400 text-[11px]">
                      {txn.paymentMethod.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                        txn.environment === 'PRODUCTION' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                        txn.environment === 'STAGING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {txn.environment}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 text-[10px] whitespace-nowrap">
                      {txn.updatedAt}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button className="px-2.5 py-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 text-[10px] font-bold transition-all">
                        INSPECT
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
