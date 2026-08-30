'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { SettlementBatchRecord } from './reconciliation-types';
import { Scale } from 'lucide-react';

interface SettlementTableProps {
  batches: SettlementBatchRecord[];
  onSelectBatch: (batch: SettlementBatchRecord) => void;
}

export function SettlementTable({ batches, onSelectBatch }: SettlementTableProps) {
  const getBadgeStatus = (status: string): AGBadgeStatus => {
    switch (status) {
      case 'MATCHED':
        return 'APPROVED';
      case 'VARIANCE':
        return 'REVIEW';
      case 'REVIEW':
        return 'PENDING';
      case 'FAILED':
        return 'BLOCKED';
      default:
        return 'ACTIVE';
    }
  };

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-400" /> GATEWAY SETTLEMENT BATCH OPERATIONS
          </h3>
          <p className="text-[10px] text-slate-400">Processor clearing file reconciliation matching payment intents</p>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="text-slate-400">Matched: <strong className="text-emerald-400 font-bold">1,284</strong></span>
          <span className="text-slate-400">Unmatched: <strong className="text-red-400 font-bold">17</strong></span>
          <span className="text-slate-400">Fee Variance: <strong className="text-amber-400 font-bold">$12,842</strong></span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Batch ID</th>
              <th className="p-3.5">Processor</th>
              <th className="p-3.5">Settlement Date</th>
              <th className="p-3.5">Gross Amount</th>
              <th className="p-3.5">Fees</th>
              <th className="p-3.5">Net Settlement</th>
              <th className="p-3.5">Matched / Unmatched</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {batches.map((b) => (
              <tr
                key={b.id}
                onClick={() => onSelectBatch(b)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">{b.id}</td>

                <td className="p-3.5 font-bold text-blue-400">{b.processor}</td>

                <td className="p-3.5 text-slate-400 text-[10px]">{b.settlementDate}</td>

                <td className="p-3.5 font-bold text-slate-200">{b.grossAmount}</td>

                <td className="p-3.5 font-bold text-red-400">{b.fees}</td>

                <td className="p-3.5 font-bold text-emerald-400">{b.netAmount}</td>

                <td className="p-3.5">
                  <span className="text-emerald-400 font-bold">{b.matchedCount}</span> / <span className={b.unmatchedCount > 0 ? 'text-red-400 font-bold' : 'text-slate-500'}>{b.unmatchedCount}</span>
                </td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(b.status)} label={`● ${b.status}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectBatch(b)}>
                    Inspect
                  </AGButton>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
