'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { ProductionAgentPermissionRecord } from './agent-types';
import { ShieldCheck } from 'lucide-react';

interface AgentPermissionsTableProps {
  permissions: ProductionAgentPermissionRecord[];
}

export function AgentPermissionsTable({ permissions }: AgentPermissionsTableProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> RBAC CAPABILITIES & SCOPE MATRIX
          </h3>
          <p className="text-[10px] text-slate-400">Zero-trust capability bindings and least-privilege resource scopes</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Agent ID</th>
              <th className="p-3.5">Resource Target</th>
              <th className="p-3.5">Capability Grant</th>
              <th className="p-3.5">Scope</th>
              <th className="p-3.5">Policy Restriction</th>
              <th className="p-3.5">Permission Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {permissions.map((p) => (
              <tr key={p.id} className="hover:bg-slate-800/40 cursor-pointer transition-colors">
                <td className="p-3.5 font-bold text-blue-400">{p.agentId}</td>

                <td className="p-3.5 font-bold text-slate-100">{p.resource}</td>

                <td className="p-3.5 text-slate-300 font-bold">{p.capability}</td>

                <td className="p-3.5 font-bold text-emerald-400">{p.scope}</td>

                <td className="p-3.5 text-slate-400 text-[10px] font-mono">{p.policyRule}</td>

                <td className="p-3.5">
                  <AGBadge status="APPROVED" label={`● ${p.status}`} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
