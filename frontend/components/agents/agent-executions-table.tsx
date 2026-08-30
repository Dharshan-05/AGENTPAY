'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { ProductionAgentExecution } from './agent-types';
import { Layers } from 'lucide-react';

interface AgentExecutionsTableProps {
  executions: ProductionAgentExecution[];
}

export function AgentExecutionsTable({ executions }: AgentExecutionsTableProps) {
  const getBadgeStatus = (result: string): AGBadgeStatus => {
    switch (result) {
      case 'AUTHORIZED':
        return 'APPROVED';
      case 'REVIEW':
        return 'REVIEW';
      case 'BLOCKED':
        return 'BLOCKED';
      case 'FAILED':
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
            <Layers className="w-4 h-4 text-blue-400" /> DURABLE AGENT EXECUTION TELEMETRY
          </h3>
          <p className="text-[10px] text-slate-400">Trigger.dev style durable execution run logs and latency tracking</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Execution ID & Timestamp</th>
              <th className="p-3.5">Agent ID</th>
              <th className="p-3.5">Intent & Action</th>
              <th className="p-3.5">Policy Evaluated</th>
              <th className="p-3.5">Risk Score</th>
              <th className="p-3.5">Latency</th>
              <th className="p-3.5">Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {executions.map((e) => (
              <tr key={e.id} className="hover:bg-slate-900/40 cursor-pointer transition-colors">
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{e.executionId}</div>
                  <div className="text-[10px] text-slate-400 font-normal">{e.timestamp}</div>
                </td>

                <td className="p-3.5 font-bold text-blue-400 font-mono">{e.agentId}</td>

                <td className="p-3.5 font-bold text-slate-200">
                  <div>{e.intent}</div>
                  <div className="text-[10px] text-slate-400 font-normal">{e.action}</div>
                </td>

                <td className="p-3.5 text-slate-400 text-[10px] font-mono">{e.policy}</td>

                <td className="p-3.5 font-bold text-emerald-400">{e.riskScore}</td>

                <td className="p-3.5 text-slate-300">{e.latencyMs}ms</td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(e.result)} label={`● ${e.result}`} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
