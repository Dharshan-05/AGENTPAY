'use client';

import { SourceAgentRecord } from './source-types';

interface SourceAgentRegistryProps {
  agents: SourceAgentRecord[];
  onSelectAgent: (agent: SourceAgentRecord) => void;
}

export function SourceAgentRegistry({ agents, onSelectAgent }: SourceAgentRegistryProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Autonomous Financial Agent Registry</h3>
          <p className="text-xs text-slate-500">Excavated identity & operational status inventory</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Agent ID & Persona</th>
              <th className="p-3">Execution Type</th>
              <th className="p-3">Owner / Department</th>
              <th className="p-3">Environment</th>
              <th className="p-3">Policy Binding</th>
              <th className="p-3">Health Score</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {agents.map((a) => (
              <tr key={a.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {a.name}
                  <div className="text-[10px] text-blue-700 font-mono font-bold">{a.agentId}</div>
                </td>
                <td className="p-3 font-bold text-slate-700 text-[10px]">{a.type}</td>
                <td className="p-3 text-slate-600 font-sans">{a.owner}</td>
                <td className="p-3 text-slate-700 font-bold">{a.environment}</td>
                <td className="p-3 text-slate-500 text-[10px] font-mono">{a.policyBinding}</td>
                <td className="p-3 font-bold text-emerald-600">{a.healthScore}%</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      a.status === 'ACTIVE'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {a.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectAgent(a)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] rounded-lg transition-colors"
                  >
                    Inspect Identity
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
