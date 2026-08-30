'use client';

import { PermissionRecord } from './source-types';
import { Sliders } from 'lucide-react';

interface SourcePermissionsProps {
  permissions: PermissionRecord[];
}

export function SourcePermissions({ permissions }: SourcePermissionsProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            Granular Permission Matrix
          </h3>
          <p className="text-xs text-slate-500">Excavated resource-level access control matrix</p>
        </div>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Resource Target</th>
              <th className="p-3">SUPER ADMIN</th>
              <th className="p-3">SECURITY OPERATOR</th>
              <th className="p-3">DEVELOPER</th>
              <th className="p-3">ANALYST</th>
              <th className="p-3">VIEWER</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {permissions.map((p) => (
              <tr key={p.resource} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">{p.resource}</td>
                <td className="p-3 font-bold text-emerald-600">{p.superAdmin}</td>
                <td className="p-3 text-blue-700 font-bold">{p.securityOperator}</td>
                <td className="p-3 text-slate-700">{p.developer}</td>
                <td className="p-3 text-slate-700">{p.analyst}</td>
                <td className="p-3 text-slate-400">{p.viewer}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
