'use client';

import { RoleRecord } from './source-types';
import { ShieldAlert, Plus } from 'lucide-react';

interface SourceRolesProps {
  roles: RoleRecord[];
  onSelectRole: (role: RoleRecord) => void;
}

export function SourceRoles({ roles, onSelectRole }: SourceRolesProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-blue-600" />
            Roles & Role-Based Access Control (RBAC)
          </h3>
          <p className="text-xs text-slate-500">Excavated security role definition matrix</p>
        </div>

        <button className="px-3.5 py-2 bg-slate-900 text-white font-semibold text-xs rounded-xl hover:bg-slate-800 flex items-center gap-1">
          <Plus className="w-3.5 h-3.5" /> Create Custom Role
        </button>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Role Name</th>
              <th className="p-3">Assigned Members</th>
              <th className="p-3">Permissions Count</th>
              <th className="p-3">Type</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {roles.map((r) => (
              <tr key={r.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {r.name}
                  <div className="text-[10px] text-slate-500 font-sans font-normal">{r.description}</div>
                </td>
                <td className="p-3 font-bold text-slate-700 font-sans">{r.membersCount} Members</td>
                <td className="p-3 font-bold text-blue-700">{r.permissionsCount} Grants</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      r.status === 'SYSTEM'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}
                  >
                    {r.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectRole(r)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] rounded-lg transition-colors"
                  >
                    Inspect Role
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
