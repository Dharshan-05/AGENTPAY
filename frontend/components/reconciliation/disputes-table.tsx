'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { DisputeRecord } from './reconciliation-types';
import { ShieldAlert } from 'lucide-react';

interface DisputesTableProps {
  disputes: DisputeRecord[];
  onSelectDispute: (dispute: DisputeRecord) => void;
}

export function DisputesTable({ disputes, onSelectDispute }: DisputesTableProps) {
  const getBadgeStatus = (status: string): AGBadgeStatus => {
    switch (status) {
      case 'WON':
        return 'APPROVED';
      case 'UNDER REVIEW':
        return 'REVIEW';
      case 'EVIDENCE PREPARING':
        return 'PENDING';
      case 'LOST':
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
            <ShieldAlert className="w-4 h-4 text-red-400" /> ACTIVE CHARGEBACKS & DISPUTES QUEUE
          </h3>
          <p className="text-[10px] text-slate-400">Agent unauthorized intent and policy violation arbitration dossiers</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Dispute ID & Txn</th>
              <th className="p-3.5">Agent Persona</th>
              <th className="p-3.5">Merchant Target</th>
              <th className="p-3.5">Dispute Amount</th>
              <th className="p-3.5">Reason Code</th>
              <th className="p-3.5">Deadline</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {disputes.map((d) => (
              <tr
                key={d.id}
                onClick={() => onSelectDispute(d)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{d.disputeId}</div>
                  <div className="text-[10px] text-slate-500 font-normal">{d.transactionId}</div>
                </td>

                <td className="p-3.5 font-bold text-blue-400">{d.agentId}</td>

                <td className="p-3.5 text-slate-300 font-bold">{d.merchant}</td>

                <td className="p-3.5 font-bold text-red-400">{d.amount}</td>

                <td className="p-3.5 text-slate-400 text-[10px]">{d.reason}</td>

                <td className="p-3.5 text-amber-400 font-bold text-[10px]">{d.deadline}</td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(d.status)} label={`● ${d.status}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectDispute(d)}>
                    Inspect Dossier
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
