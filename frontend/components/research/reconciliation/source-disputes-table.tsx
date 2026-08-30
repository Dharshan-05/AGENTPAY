'use client';

import { SourceDisputeRecord } from './source-types';

interface SourceDisputesTableProps {
  disputes: SourceDisputeRecord[];
  onSelectDispute: (dispute: SourceDisputeRecord) => void;
}

export function SourceDisputesTable({ disputes, onSelectDispute }: SourceDisputesTableProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Chargeback & Dispute Arbitration Pipeline</h3>
          <p className="text-xs text-slate-500">Excavated dispute state machine & evidence submission log</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Dispute ID & Txn</th>
              <th className="p-3">Agent Persona</th>
              <th className="p-3">Merchant Target</th>
              <th className="p-3">Dispute Amount</th>
              <th className="p-3">Reason Code</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {disputes.map((d) => (
              <tr key={d.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {d.disputeId}
                  <div className="text-[10px] text-slate-500 font-mono font-normal">{d.transactionId}</div>
                </td>
                <td className="p-3 font-bold text-blue-700 font-mono">{d.agentId}</td>
                <td className="p-3 text-slate-700 font-sans">{d.merchant}</td>
                <td className="p-3 font-bold text-rose-600">{d.amount}</td>
                <td className="p-3 text-slate-600 text-[10px]">{d.reason}</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      d.status === 'WON'
                        ? 'bg-emerald-100 text-emerald-800'
                        : d.status === 'UNDER_REVIEW'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {d.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectDispute(d)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] rounded-lg transition-colors"
                  >
                    Inspect Dossier
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
