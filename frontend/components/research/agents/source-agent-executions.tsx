'use client';

import { SourceAgentExecution } from './source-types';

interface SourceAgentExecutionsProps {
  executions: SourceAgentExecution[];
}

export function SourceAgentExecutions({ executions }: SourceAgentExecutionsProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Durable Agent Execution Telemetry</h3>
          <p className="text-xs text-slate-500">Excavated Trigger.dev / OpenHands execution run history</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Execution ID & Timestamp</th>
              <th className="p-3">Agent ID</th>
              <th className="p-3">Intent & Action</th>
              <th className="p-3">Policy Evaluated</th>
              <th className="p-3">Risk Score</th>
              <th className="p-3">Latency</th>
              <th className="p-3">Execution Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {executions.map((e) => (
              <tr key={e.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900">
                  {e.executionId}
                  <div className="text-[10px] text-slate-500 font-normal">{e.timestamp}</div>
                </td>
                <td className="p-3 font-bold text-blue-700 font-mono">{e.agentId}</td>
                <td className="p-3 font-bold text-slate-800">
                  {e.intent}
                  <div className="text-[10px] text-slate-500 font-normal">{e.action}</div>
                </td>
                <td className="p-3 text-slate-600 font-mono">{e.policy}</td>
                <td className="p-3 font-bold text-emerald-600">{e.riskScore}</td>
                <td className="p-3 text-slate-700">{e.latencyMs}ms</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      e.result === 'AUTHORIZED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {e.result}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
