'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionSessionRecord } from './settings-types';
import { Smartphone, Monitor, ShieldAlert } from 'lucide-react';

interface SettingsSessionsProps {
  sessions: ProductionSessionRecord[];
  onRevokeSession: (id: string) => void;
  onRevokeAllOtherSessions: () => void;
}

export function SettingsSessions({
  sessions,
  onRevokeSession,
  onRevokeAllOtherSessions,
}: SettingsSessionsProps) {
  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-white/[0.08] gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Smartphone className="w-4 h-4 text-blue-400" /> ACTIVE USER SESSIONS & AUTHORIZED DEVICES
          </h3>
          <p className="text-[10px] text-slate-400">Cryptographically bound administrative session tokens</p>
        </div>

        <AGButton variant="danger" size="sm" onClick={onRevokeAllOtherSessions}>
          REVOKE ALL OTHER SESSIONS
        </AGButton>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Device & Browser</th>
              <th className="p-3.5">Session ID</th>
              <th className="p-3.5">Location</th>
              <th className="p-3.5">IP Address</th>
              <th className="p-3.5">Last Active</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {sessions.map((s) => (
              <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-3.5 font-bold text-slate-100">
                  <div>{s.device}</div>
                  <div className="text-[10px] text-slate-500 font-normal">{s.browser}</div>
                </td>

                <td className="p-3.5 text-emerald-400 font-bold">{s.id}</td>

                <td className="p-3.5 text-slate-300">{s.location}</td>

                <td className="p-3.5 text-blue-400 font-bold">{s.ipAddress}</td>

                <td className="p-3.5 text-slate-400 text-[10px]">{s.lastActive}</td>

                <td className="p-3.5">
                  <AGBadge
                    status={s.status === 'CURRENT' ? 'APPROVED' : 'ACTIVE'}
                    label={`● ${s.status}`}
                  />
                </td>

                <td className="p-3.5 text-right">
                  {s.status !== 'CURRENT' && (
                    <AGButton variant="danger" size="sm" onClick={() => onRevokeSession(s.id)}>
                      Revoke
                    </AGButton>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AGCard>
  );
}
