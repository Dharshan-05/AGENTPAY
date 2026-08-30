'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionAuditEventRecord } from './settings-types';
import { FileCode2 } from 'lucide-react';

interface SettingsAuditProps {
  logs: ProductionAuditEventRecord[];
  onSelectAudit: (audit: ProductionAuditEventRecord) => void;
}

export function SettingsAudit({ logs, onSelectAudit }: SettingsAuditProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-blue-400" /> SYSTEM AUDIT TELEMETRY STREAM
          </h3>
          <p className="text-[10px] text-slate-400">Cryptographically signed security audit trail entries</p>
        </div>
        <AGBadge status="POLICY_SECURE" label="IMMUTABLE LEDGER" />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Timestamp</th>
              <th className="p-3.5">Event Name</th>
              <th className="p-3.5">Actor ID</th>
              <th className="p-3.5">Resource</th>
              <th className="p-3.5">IP Address</th>
              <th className="p-3.5">Result</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {logs.map((l) => (
              <tr
                key={l.id}
                onClick={() => onSelectAudit(l)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 text-slate-400 text-[10px]">{l.timestamp}</td>

                <td className="p-3.5 font-bold text-blue-400">{l.event}</td>

                <td className="p-3.5 font-bold text-slate-100">{l.actor}</td>

                <td className="p-3.5 text-slate-300">{l.resource}</td>

                <td className="p-3.5 text-slate-400 font-mono text-[11px]">{l.ipAddress}</td>

                <td className="p-3.5">
                  <AGBadge status="APPROVED" label={`● ${l.result}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectAudit(l)}>
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
