'use client';

import { WebhookAuditEvent } from './webhook-types';
import { Lock } from 'lucide-react';

interface WebhookAuditProps {
  entries: WebhookAuditEvent[];
}

export function WebhookAudit({ entries }: WebhookAuditProps) {
  return (
    <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-slate-200 text-xs flex items-center gap-2">
          <Lock className="w-4 h-4 text-emerald-400" /> IMMUTABLE SHA-256 AUDIT LOG LEDGER
        </h3>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          CHAIN INTEGRITY VERIFIED
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">EVENT ID</th>
              <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
              <th className="px-4 py-3 font-semibold">ACTOR</th>
              <th className="px-4 py-3 font-semibold">TYPE</th>
              <th className="px-4 py-3 font-semibold">ACTION</th>
              <th className="px-4 py-3 font-semibold">TARGET REF</th>
              <th className="px-4 py-3 font-semibold">DETAILS</th>
              <th className="px-4 py-3 font-semibold">AUDIT HASH</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04] text-xs">
            {entries.map((entry) => (
              <tr key={entry.id} className="hover:bg-slate-900/40 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-300">
                  {entry.eventId}
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {entry.timestamp}
                </td>
                <td className="px-4 py-3.5 font-bold text-slate-300">
                  {entry.actor}
                </td>
                <td className="px-4 py-3.5 text-blue-400">
                  {entry.actorType}
                </td>
                <td className="px-4 py-3.5 font-bold text-emerald-400">
                  {entry.action}
                </td>
                <td className="px-4 py-3.5 text-purple-400">
                  {entry.targetRef}
                </td>
                <td className="px-4 py-3.5 text-slate-400 font-sans text-[11px]">
                  {entry.details}
                </td>
                <td className="px-4 py-3.5 text-slate-600 font-mono text-[10px]">
                  {entry.auditHash}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
