'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionMemberRecord } from './settings-types';
import { Users, UserPlus } from 'lucide-react';

interface SettingsMembersProps {
  members: ProductionMemberRecord[];
  onSelectMember: (member: ProductionMemberRecord) => void;
  onOpenInviteModal: () => void;
  onSuspendMember: (id: string) => void;
}

export function SettingsMembers({
  members,
  onSelectMember,
  onOpenInviteModal,
  onSuspendMember,
}: SettingsMembersProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400" /> TEAM MEMBERS & ZERO-TRUST ACCESS CONTROL
          </h3>
          <p className="text-[10px] text-slate-400">Manage administrative users, role assignments, and MFA enforcement</p>
        </div>

        <AGButton variant="primary" size="sm" icon={UserPlus} onClick={onOpenInviteModal}>
          INVITE MEMBER
        </AGButton>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Member Name & Email</th>
              <th className="p-3.5">Role</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">MFA</th>
              <th className="p-3.5">Joined</th>
              <th className="p-3.5">Last Active</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {members.map((m) => (
              <tr
                key={m.id}
                onClick={() => onSelectMember(m)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{m.name}</div>
                  <div className="text-[10px] text-slate-500 font-normal">{m.email}</div>
                </td>

                <td className="p-3.5 font-bold text-blue-400">{m.role}</td>

                <td className="p-3.5">
                  <AGBadge
                    status={m.status === 'ACTIVE' ? 'APPROVED' : 'PENDING'}
                    label={`● ${m.status}`}
                  />
                </td>

                <td className="p-3.5 font-bold text-emerald-400">
                  {m.mfaEnforced ? 'ENFORCED' : 'OPTIONAL'}
                </td>

                <td className="p-3.5 text-slate-400 text-[10px]">{m.joinedDate}</td>

                <td className="p-3.5 text-slate-400 text-[10px]">{m.lastActive}</td>

                <td className="p-3.5 text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-end gap-2">
                    <AGButton variant="ghost" size="sm" onClick={() => onSelectMember(m)}>
                      Inspect
                    </AGButton>
                    {m.status !== 'SUSPENDED' && (
                      <AGButton variant="danger" size="sm" onClick={() => onSuspendMember(m.id)}>
                        Suspend
                      </AGButton>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
