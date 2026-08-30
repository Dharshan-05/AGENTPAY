'use client';

import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionMemberRecord } from './settings-types';
import { ShieldCheck, Mail, Calendar, Clock } from 'lucide-react';

interface MemberInspectorProps {
  member: ProductionMemberRecord | null;
  onClose: () => void;
  onSuspend: (id: string) => void;
}

export function MemberInspector({ member, onClose, onSuspend }: MemberInspectorProps) {
  if (!member) return null;

  return (
    <AGDrawer
      isOpen={!!member}
      onClose={onClose}
      title={`MEMBER INSPECTOR: ${member.name}`}
      subtitle="ZERO-TRUST TEAM MEMBER IDENTITY & ACCESS SCOPE"
      footer={
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-2 gap-2">
            {member.status !== 'SUSPENDED' && (
              <AGButton variant="danger" size="md" onClick={() => onSuspend(member.id)}>
                SUSPEND MEMBER
              </AGButton>
            )}
            <AGButton variant="secondary" size="md" onClick={onClose}>
              CLOSE INSPECTOR
            </AGButton>
          </div>
        </div>
      }
    >
      <div className="space-y-6 font-mono text-xs">
        <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">MEMBER STATUS</span>
            <span className="text-base font-bold text-slate-100">{member.status}</span>
          </div>
          <AGBadge status={member.status === 'ACTIVE' ? 'APPROVED' : 'PENDING'} label={`● ${member.status}`} />
        </div>

        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 space-y-2 text-[11px]">
          <div className="flex justify-between">
            <span className="text-slate-400">Member ID:</span>
            <span className="text-blue-400 font-bold">{member.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Email Address:</span>
            <span className="text-slate-200 font-bold">{member.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Assigned Role:</span>
            <span className="text-emerald-400 font-bold">{member.role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">MFA Enforced:</span>
            <span className="text-emerald-400 font-bold">{member.mfaEnforced ? 'ENFORCED' : 'OPTIONAL'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Joined Date:</span>
            <span className="text-slate-400">{member.joinedDate}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Last Active:</span>
            <span className="text-slate-300">{member.lastActive}</span>
          </div>
        </div>
      </div>
    </AGDrawer>
  );
}
