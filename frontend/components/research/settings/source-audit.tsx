'use client';

import { AuditLogRecord } from './source-types';
import { FileCode2 } from 'lucide-react';

interface SourceAuditProps {
  logs: AuditLogRecord[];
  onSelectLog: (log: AuditLogRecord) => void;
}

export function SourceAudit({ logs, onSelectLog }: SourceAuditProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-blue-600" />
            Security & System Audit Activity Stream
          </h3>
          <p className="text-xs text-slate-500">Excavated security audit log table</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Audit Event</th>
              <th className="p-3">Actor / User</th>
              <th className="p-3">Target Resource</th>
              <th className="p-3">IP Address</th>
              <th className="p-3">Timestamp</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {logs.map((l) => (
              <tr key={l.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-blue-700 font-sans">{l.event}</td>
                <td className="p-3 font-bold text-slate-900">{l.actor}</td>
                <td className="p-3 text-slate-700">{l.resource}</td>
                <td className="p-3 text-slate-500">{l.ipAddress}</td>
                <td className="p-3 text-slate-500 text-[10px]">{l.timestamp}</td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectLog(l)}
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
