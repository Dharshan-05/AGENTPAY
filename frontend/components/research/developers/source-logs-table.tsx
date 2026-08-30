'use client';

import { SourceDeveloperLogRecord } from './source-types';
import { FileCode2 } from 'lucide-react';

interface SourceLogsTableProps {
  logs: SourceDeveloperLogRecord[];
}

export function SourceLogsTable({ logs }: SourceLogsTableProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-blue-600" />
            API Request & Audit Logs Stream
          </h3>
          <p className="text-xs text-slate-500">Excavated developer HTTP request telemetry table</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Method</th>
              <th className="p-3">Endpoint Route</th>
              <th className="p-3">Status</th>
              <th className="p-3">Latency</th>
              <th className="p-3">IP Address / Node</th>
              <th className="p-3">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {logs.map((l) => (
              <tr key={l.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] ${
                      l.method === 'POST'
                        ? 'bg-blue-100 text-blue-800'
                        : l.method === 'GET'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {l.method}
                  </span>
                </td>
                <td className="p-3 font-bold text-slate-900">{l.endpoint}</td>
                <td className="p-3 font-bold text-emerald-600">{l.statusCode} OK</td>
                <td className="p-3 text-slate-500">{l.latency}</td>
                <td className="p-3 text-slate-500 text-[10px]">{l.ipAddress}</td>
                <td className="p-3 text-slate-500 text-[10px]">{l.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
