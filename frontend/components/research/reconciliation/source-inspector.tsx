'use client';

import { SourceSettlementBatch, SourceDisputeRecord } from './source-types';
import { X, Scale, FileText, Check } from 'lucide-react';

interface SourceInspectorProps {
  batchItem: SourceSettlementBatch | null;
  disputeItem: SourceDisputeRecord | null;
  onClose: () => void;
}

export function SourceInspector({ batchItem, disputeItem, onClose }: SourceInspectorProps) {
  if (!batchItem && !disputeItem) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end font-sans">
      <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto space-y-6 text-slate-800">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">SOURCE INSPECTOR</span>
              <h2 className="text-lg font-bold text-slate-900">
                {batchItem?.id || disputeItem?.disputeId}
              </h2>
            </div>
            <button onClick={onClose} className="p-1 rounded hover:bg-slate-100 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          {batchItem && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between"><span className="text-slate-500">Processor:</span><span className="font-bold text-slate-900 font-sans">{batchItem.processor}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Gross Settlement:</span><span className="font-bold text-slate-900">{batchItem.grossAmount}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Processing Fees:</span><span className="font-bold text-rose-600">{batchItem.feeAmount}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Net Deposit:</span><span className="font-bold text-emerald-600">{batchItem.netAmount}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Matched Count:</span><span className="font-bold text-blue-600">{batchItem.matchedCount} Txns</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Unmatched Variances:</span><span className="font-bold text-rose-600">{batchItem.unmatchedCount} Items</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Settlement Date:</span><span className="text-slate-600">{batchItem.settlementDate}</span></div>
            </div>
          )}

          {disputeItem && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between"><span className="text-slate-500">Transaction ID:</span><span className="font-bold text-slate-900">{disputeItem.transactionId}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Agent Persona:</span><span className="font-bold text-blue-600">{disputeItem.agentId}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Merchant Target:</span><span className="font-bold text-slate-800 font-sans">{disputeItem.merchant}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Disputed Amount:</span><span className="font-bold text-rose-600">{disputeItem.amount}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Reason Code:</span><span className="text-slate-700">{disputeItem.reason}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Dispute Status:</span><span className="font-bold text-emerald-600">{disputeItem.status}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Evidence Deadline:</span><span className="text-amber-600 font-bold">{disputeItem.evidenceDeadline}</span></div>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-xl text-xs hover:bg-slate-800 transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
