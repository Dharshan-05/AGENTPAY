'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AgentPerformanceRecord } from './analytics-types';
import { Users, ChevronRight } from 'lucide-react';
import Link from 'next/link';

interface AgentPerformanceProps {
  agents: AgentPerformanceRecord[];
}

export function AgentPerformance({ agents }: AgentPerformanceProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2 font-bold text-slate-100">
          <Users className="w-4 h-4 text-blue-400" />
          <span className="text-sm">AGENT PERFORMANCE TELEMETRY</span>
        </div>
        <span className="text-[10px] text-slate-400">Ranked by Transaction Volume</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Agent Persona</th>
              <th className="p-3.5">Transactions</th>
              <th className="p-3.5">Success Rate</th>
              <th className="p-3.5">Avg Risk</th>
              <th className="p-3.5">Policy Triggers</th>
              <th className="p-3.5">Total Value</th>
              <th className="p-3.5 text-right">Decision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {agents.map((a) => (
              <tr key={a.agentId} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-3.5 font-bold text-slate-100">
                  {a.agentName} <div className="text-[10px] text-slate-500 font-normal">({a.agentId})</div>
                </td>
                <td className="p-3.5 text-slate-200 font-bold">{a.transactions}</td>
                <td className="p-3.5 text-emerald-400 font-bold">{a.successRate}</td>
                <td className="p-3.5 font-bold text-amber-400">{a.avgRisk}</td>
                <td className="p-3.5 text-slate-400">{a.policyViolations}</td>
                <td className="p-3.5 font-bold text-emerald-400">{a.totalValue}</td>
                <td className="p-3.5 text-right">
                  <AGBadge
                    status={
                      a.decision === 'AUTHORIZED'
                        ? 'APPROVED'
                        : a.decision === 'BLOCKED'
                        ? 'BLOCKED'
                        : 'REVIEW'
                    }
                    label={a.decision}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
