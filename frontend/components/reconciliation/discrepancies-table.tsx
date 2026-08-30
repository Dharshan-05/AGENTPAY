'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DiscrepancyRecord } from './reconciliation-types';
import { AlertTriangle } from 'lucide-react';

interface DiscrepanciesTableProps {
  discrepancies: DiscrepancyRecord[];
  onSelectDiscrepancy: (discrepancy: DiscrepancyRecord) => void;
}

export function DiscrepanciesTable({ discrepancies, onSelectDiscrepancy }: DiscrepanciesTableProps) {
  const getBadgeStatus = (severity: string): AGBadgeStatus => {
    switch (severity) {
      case 'CRITICAL':
        return 'BLOCKED';
      case 'HIGH':
        return 'REVIEW';
      case 'MEDIUM':
        return 'PENDING';
      default:
        return 'ACTIVE';
    }
  };

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> UNRESOLVED VARIANCE INVESTIGATION CONSOLE
          </h3>
          <p className="text-[10px] text-slate-400">Discrepancies between AGENTPAY Intent, Gateway Clearing, and Ledger</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Variance ID & Txn</th>
              <th className="p-3.5">Agent Persona</th>
              <th className="p-3.5">Processor</th>
              <th className="p-3.5">Expected</th>
              <th className="p-3.5">Actual Settled</th>
              <th className="p-3.5">Delta</th>
              <th className="p-3.5">Variance Type</th>
              <th className="p-3.5">Severity</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {discrepancies.map((d) => (
              <tr
                key={d.id}
                onClick={() => onSelectDiscrepancy(d)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{d.varianceId}</div>
                  <div className="text-[10px] text-slate-500 font-normal">{d.transactionId}</div>
                </td>

                <td className="p-3.5 font-bold text-blue-400">{d.agentId}</td>

                <td className="p-3.5 text-slate-300 font-bold">{d.processor}</td>

                <td className="p-3.5 font-bold text-slate-200">{d.expectedAmount}</td>

                <td className="p-3.5 font-bold text-emerald-400">{d.actualAmount}</td>

                <td className="p-3.5 font-bold text-red-400">{d.deltaAmount}</td>

                <td className="p-3.5 text-slate-400 text-[10px]">{d.type}</td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(d.severity)} label={`● ${d.severity}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectDiscrepancy(d)}>
                    Inspect Delta
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
