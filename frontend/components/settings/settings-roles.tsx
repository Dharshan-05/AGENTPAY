'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionRoleRecord } from './settings-types';
import { ShieldAlert, Plus } from 'lucide-react';

interface SettingsRolesProps {
  roles: ProductionRoleRecord[];
  onSelectRole: (role: ProductionRoleRecord) => void;
}

export function SettingsRoles({ roles, onSelectRole }: SettingsRolesProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-blue-400" /> ROLE-BASED ACCESS CONTROL (RBAC)
          </h3>
          <p className="text-[10px] text-slate-400">System and custom role definitions governing user authorization</p>
        </div>

        <AGButton variant="secondary" size="sm" icon={Plus} onClick={() => alert('Custom role creation simulation')}>
          CREATE CUSTOM ROLE
        </AGButton>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Role Name</th>
              <th className="p-3.5">Assigned Members</th>
              <th className="p-3.5">Permissions Count</th>
              <th className="p-3.5">Environments</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {roles.map((r) => (
              <tr
                key={r.id}
                onClick={() => onSelectRole(r)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{r.name}</div>
                  <div className="text-[10px] text-slate-500 font-normal">{r.description}</div>
                </td>

                <td className="p-3.5 text-slate-300 font-bold">{r.membersCount} Users</td>

                <td className="p-3.5 text-emerald-400 font-bold">{r.permissionsCount} Grants</td>

                <td className="p-3.5 text-blue-400 font-bold">{r.environments}</td>

                <td className="p-3.5">
                  <AGBadge status="POLICY_SECURE" label={`● ${r.status}`} />
                </td>

                <td className="p-3.5 text-right">
                  <AGButton variant="ghost" size="sm" onClick={() => onSelectRole(r)}>
                    Inspect
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
