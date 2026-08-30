'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge, AGBadgeStatus } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionAgentRecord } from './agent-types';
import { Bot } from 'lucide-react';

interface AgentRegistryTableProps {
  agents: ProductionAgentRecord[];
  onSelectAgent: (agent: ProductionAgentRecord) => void;
}

export function AgentRegistryTable({ agents, onSelectAgent }: AgentRegistryTableProps) {
  const getBadgeStatus = (status: string): AGBadgeStatus => {
    switch (status) {
      case 'ACTIVE':
        return 'APPROVED';
      case 'IDLE':
        return 'ACTIVE';
      case 'SUSPENDED':
        return 'BLOCKED';
      case 'DEGRADED':
        return 'REVIEW';
      default:
        return 'PENDING';
    }
  };

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Bot className="w-4 h-4 text-blue-400" /> AUTONOMOUS FINANCIAL AGENT INVENTORY
          </h3>
          <p className="text-[10px] text-slate-400">First-class zero-trust agent identities governed by AGENTGUARD policies</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Agent ID & Name</th>
              <th className="p-3.5">Type</th>
              <th className="p-3.5">Owner / Department</th>
              <th className="p-3.5">Environment</th>
              <th className="p-3.5">Policy Binding</th>
              <th className="p-3.5">Health Score</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {agents.map((a) => (
              <tr
                key={a.id}
                onClick={() => onSelectAgent(a)}
                className="hover:bg-slate-900/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{a.name}</div>
                  <div className="text-[10px] text-blue-400 font-bold">{a.agentId}</div>
                </td>

                <td className="p-3.5 font-bold text-slate-300 text-[10px]">{a.type}</td>

                <td className="p-3.5 text-slate-300 font-bold">{a.owner}</td>

                <td className="p-3.5 text-slate-200 font-bold">{a.environment}</td>

                <td className="p-3.5 text-slate-400 text-[10px] font-mono">{a.policyBinding}</td>

                <td className="p-3.5 font-bold text-emerald-400">{a.healthScore}%</td>

                <td className="p-3.5">
                  <AGBadge status={getBadgeStatus(a.status)} label={`● ${a.status}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectAgent(a)}>
                    Inspect Identity
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
