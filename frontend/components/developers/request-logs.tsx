'use client';

import { AGCard } from '@/components/ui/ag-card';
import { DeveloperRequestLog } from './developers-types';
import { FileCode2 } from 'lucide-react';
import { AGButton } from '@/components/ui/ag-button';

interface RequestLogsProps {
  logs: DeveloperRequestLog[];
  onSelectLog: (log: DeveloperRequestLog) => void;
}

export function RequestLogs({ logs, onSelectLog }: RequestLogsProps) {
  return (
    <div className="space-y-6 font-mono text-xs">
      <AGCard className="space-y-4">
        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <FileCode2 className="w-4 h-4 text-blue-400" /> HTTP REQUEST & AUDIT TELEMETRY STREAM
            </h3>
            <p className="text-[10px] text-slate-400">Real-time developer API request logs with mTLS and security policy evaluations</p>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold">184,291 Total Requests 24H</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
                <th className="p-3.5">Method</th>
                <th className="p-3.5">Request ID & Route</th>
                <th className="p-3.5">Agent Persona</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Latency</th>
                <th className="p-3.5">Risk Score</th>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {logs.map((l) => (
                <tr
                  key={l.id}
                  onClick={() => onSelectLog(l)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="p-3.5">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        l.method === 'POST'
                          ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                          : l.method === 'GET'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-red-500/10 text-red-400 border-red-500/30'
                      }`}
                    >
                      {l.method}
                    </span>
                  </td>

                  <td className="p-3.5 font-bold text-slate-100">
                    <div>{l.endpoint}</div>
                    <div className="text-[10px] text-slate-500 font-normal">{l.requestId}</div>
                  </td>

                  <td className="p-3.5 text-slate-300 font-bold">{l.agentId}</td>

                  <td className="p-3.5 font-bold text-emerald-400">{l.statusCode} OK</td>

                  <td className="p-3.5 text-slate-400">{l.latency}</td>

                  <td className="p-3.5 font-bold text-amber-400">{l.riskScore}</td>

                  <td className="p-3.5 text-slate-400 text-[10px]">{l.timestamp}</td>

                  <td className="p-3.5 text-right">
                    <AGButton variant="ghost" size="sm">
                      Inspect
                    </AGButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AGCard>
    </div>
  );
}
