'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionRoleRecord } from './settings-types';
import { ShieldAlert, Layers } from 'lucide-react';

interface RoleInspectorProps {
  role: ProductionRoleRecord | null;
  onClose: () => void;
}

export function RoleInspector({ role, onClose }: RoleInspectorProps) {
  if (!role) return null;

  return (
    <AGDrawer
      isOpen={!!role}
      onClose={onClose}
      title={`ROLE INSPECTOR: ${role.name}`}
      subtitle="ROLE-BASED ACCESS CONTROL (RBAC) SCOPE DEFINITION"
      footer={
        <div className="space-y-3 font-mono">
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE INSPECTOR
          </AGButton>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">ROLE TYPE</span>
            <span className="text-base font-bold text-blue-400">{role.status}</span>
          </div>
          <AGBadge status="POLICY_SECURE" label={`● ${role.permissionsCount} GRANTS`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Role ID:</span>
            <span className="text-slate-200 font-bold">{role.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Assigned Members:</span>
            <span className="text-emerald-400 font-bold">{role.membersCount} Users</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Allowed Environments:</span>
            <span className="text-blue-400 font-bold">{role.environments}</span>
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
            ROLE DESCRIPTION & SCOPE
          </h4>
          <p className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] text-slate-300 leading-relaxed text-[11px]">
            {role.description}
          </p>
        </div>
      </div>
    </AGDrawer>
  );
}
