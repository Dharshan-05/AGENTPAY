'use client';

import { SourceSettlementBatch } from './source-types';

interface SourceReconciliationTableProps {
  batches: SourceSettlementBatch[];
  onSelectBatch: (batch: SourceSettlementBatch) => void;
}

export function SourceReconciliationTable({ batches, onSelectBatch }: SourceReconciliationTableProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Gateway Settlement Batch Matching</h3>
          <p className="text-xs text-slate-500">Excavated multi-processor settlement matching table</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Batch ID & Processor</th>
              <th className="p-3">Gross Amount</th>
              <th className="p-3">Processing Fees</th>
              <th className="p-3">Net Settlement</th>
              <th className="p-3">Matched / Unmatched</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {batches.map((b) => (
              <tr key={b.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {b.processor}
                  <div className="text-[10px] text-slate-500 font-mono font-normal">{b.id}</div>
                </td>
                <td className="p-3 font-bold text-slate-900">{b.grossAmount}</td>
                <td className="p-3 text-rose-600">{b.feeAmount}</td>
                <td className="p-3 font-bold text-emerald-600">{b.netAmount}</td>
                <td className="p-3 text-slate-700">
                  <span className="font-bold text-emerald-600">{b.matchedCount}</span> / <span className={b.unmatchedCount > 0 ? 'text-rose-600 font-bold' : 'text-slate-400'}>{b.unmatchedCount}</span>
                </td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      b.status === 'MATCHED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {b.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectBatch(b)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] rounded-lg transition-colors"
                  >
                    Inspect
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
