'use client';

import { WebhookAuditEvent } from './source-types';

interface SourceAuditProps {
  entries: WebhookAuditEvent[];
}

export function SourceAudit({ entries }: SourceAuditProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden font-sans">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
              <th className="px-4 py-3 font-semibold">EVENT ID</th>
              <th className="px-4 py-3 font-semibold">TIMESTAMP</th>
              <th className="px-4 py-3 font-semibold">ACTOR</th>
              <th className="px-4 py-3 font-semibold">ACTOR TYPE</th>
              <th className="px-4 py-3 font-semibold">ACTION</th>
              <th className="px-4 py-3 font-semibold">TARGET REF</th>
              <th className="px-4 py-3 font-semibold">DETAILS</th>
              <th className="px-4 py-3 font-semibold">AUDIT HASH</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-xs">
            {entries.map((entry) => (
              <tr key={entry.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3.5 font-bold text-slate-800">
                  {entry.eventId}
                </td>
                <td className="px-4 py-3.5 text-slate-500 text-[10px]">
                  {entry.timestamp}
                </td>
                <td className="px-4 py-3.5 font-bold text-slate-700">
                  {entry.actor}
                </td>
                <td className="px-4 py-3.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    entry.actorType === 'DEVELOPER' ? 'bg-purple-50 text-purple-700 border-purple-200' :
                    entry.actorType === 'AUTOMATION' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    'bg-slate-100 text-slate-600 border-slate-200'
                  }`}>
                    {entry.actorType}
                  </span>
                </td>
                <td className="px-4 py-3.5 font-bold text-purple-800">
                  {entry.action}
                </td>
                <td className="px-4 py-3.5 text-blue-600 font-bold">
                  {entry.targetRef}
                </td>
                <td className="px-4 py-3.5 text-slate-600 text-[11px]">
                  {entry.details}
                </td>
                <td className="px-4 py-3.5 text-[10px] text-slate-400 font-mono">
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
