'use client';

import { OrganizationMemberRecord } from './source-types';
import { Users, UserPlus } from 'lucide-react';

interface SourceMembersProps {
  members: OrganizationMemberRecord[];
  onSelectMember: (member: OrganizationMemberRecord) => void;
  onOpenInviteModal: () => void;
}

export function SourceMembers({ members, onSelectMember, onOpenInviteModal }: SourceMembersProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            Team Members & Access Control
          </h3>
          <p className="text-xs text-slate-500">Excavated team members administration table</p>
        </div>

        <button
          onClick={onOpenInviteModal}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
        >
          <UserPlus className="w-3.5 h-3.5" /> Invite Member
        </button>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Member Name & Email</th>
              <th className="p-3">Assigned Role</th>
              <th className="p-3">Status</th>
              <th className="p-3">Last Active</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {members.map((m) => (
              <tr key={m.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {m.name} <div className="text-[10px] text-slate-500 font-mono">{m.email}</div>
                </td>
                <td className="p-3 font-bold text-blue-700 font-sans">{m.role}</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      m.status === 'ACTIVE'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {m.status}
                  </span>
                </td>
                <td className="p-3 text-slate-500 text-[10px]">{m.lastActive}</td>
                <td className="p-3 text-right font-sans">
                  <button
                    onClick={() => onSelectMember(m)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] rounded-lg transition-colors"
                  >
                    Inspect
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
