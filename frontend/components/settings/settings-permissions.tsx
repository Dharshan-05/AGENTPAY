'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { ProductionPermissionRecord } from './settings-types';
import { Sliders } from 'lucide-react';

interface SettingsPermissionsProps {
  permissions: ProductionPermissionRecord[];
}

export function SettingsPermissions({ permissions }: SettingsPermissionsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-400" /> GRANULAR RESOURCE PERMISSION MATRIX
          </h3>
          <p className="text-[10px] text-slate-400">Resource access levels across platform system roles</p>
        </div>
        <AGBadge status="POLICY_SECURE" label="ENFORCED" />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Resource Module</th>
              <th className="p-3.5">SUPER ADMIN</th>
              <th className="p-3.5">SECURITY OPERATOR</th>
              <th className="p-3.5">DEVELOPER</th>
              <th className="p-3.5">ANALYST</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {permissions.map((p) => (
              <tr key={p.resource} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-3.5 font-bold text-slate-100">{p.resource}</td>

                <td className="p-3.5 font-bold text-emerald-400">{p.superAdmin}</td>

                <td className="p-3.5 font-bold text-blue-400">{p.securityOperator}</td>

                <td className="p-3.5 font-bold text-slate-300">{p.developer}</td>

                <td className="p-3.5 font-bold text-slate-400">
                  <span className={p.analyst === 'DENIED' ? 'text-red-400' : 'text-slate-400'}>
                    {p.analyst}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
