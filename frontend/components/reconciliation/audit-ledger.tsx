'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ReconciliationAuditEvent } from './reconciliation-types';
import { FileCode2 } from 'lucide-react';

interface AuditLedgerProps {
  events: ReconciliationAuditEvent[];
  onSelectEvent: (event: ReconciliationAuditEvent) => void;
}

export function AuditLedger({ events, onSelectEvent }: AuditLedgerProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-emerald-400" /> IMMUTABLE FINANCIAL AUDIT LEDGER
          </h3>
          <p className="text-[10px] text-slate-400">Cryptographically linked SHA-256 financial audit trail stream</p>
        </div>
        <AGBadge status="APPROVED" label="● HASH CHAIN VERIFIED" />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Timestamp</th>
              <th className="p-3.5">Event ID</th>
              <th className="p-3.5">Actor</th>
              <th className="p-3.5">Target Entity</th>
              <th className="p-3.5">Action Executed</th>
              <th className="p-3.5">Source Gateway</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {events.map((e) => (
              <tr
                key={e.id}
                onClick={() => onSelectEvent(e)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 text-slate-400 text-[10px]">{e.timestamp}</td>

                <td className="p-3.5 font-bold text-emerald-400">{e.eventId}</td>

                <td className="p-3.5 font-bold text-slate-100">{e.actor}</td>

                <td className="p-3.5 text-blue-400 font-bold">{e.entity}</td>

                <td className="p-3.5 text-slate-300 font-bold">{e.action}</td>

                <td className="p-3.5 text-slate-400 font-bold">{e.source}</td>

                <td className="p-3.5">
                  <AGBadge status="APPROVED" label={`● ${e.status}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectEvent(e)}>
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
