'use client';

import { ActiveSessionRecord } from './source-types';
import { Smartphone, Monitor, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface SourceSessionsProps {
  sessions: ActiveSessionRecord[];
  onRevokeSession: (id: string) => void;
  onRevokeAllOtherSessions: () => void;
}

export function SourceSessions({ sessions, onRevokeSession, onRevokeAllOtherSessions }: SourceSessionsProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Smartphone className="w-4 h-4 text-blue-600" />
            Active User Sessions & Devices
          </h3>
          <p className="text-xs text-slate-500">Excavated session revocation table architecture</p>
        </div>

        <button
          onClick={onRevokeAllOtherSessions}
          className="px-3 py-1.5 bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold border border-rose-200 text-xs rounded-xl transition-colors"
        >
          Revoke All Other Sessions
        </button>
      </div>

      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
              <th className="p-3">Device & Browser</th>
              <th className="p-3">Location</th>
              <th className="p-3">IP Address</th>
              <th className="p-3">Last Active</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sessions.map((s) => (
              <tr key={s.id} className="hover:bg-slate-50">
                <td className="p-3 font-bold text-slate-900 font-sans">
                  {s.device} <div className="text-[10px] text-slate-500 font-mono">{s.browser}</div>
                </td>
                <td className="p-3 text-slate-700 font-sans">{s.location}</td>
                <td className="p-3 font-bold text-blue-700">{s.ipAddress}</td>
                <td className="p-3 text-slate-500 text-[10px]">{s.lastActive}</td>
                <td className="p-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      s.status === 'CURRENT'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {s.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  {s.status !== 'CURRENT' && (
                    <button
                      onClick={() => onRevokeSession(s.id)}
                      className="px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold rounded-lg hover:bg-rose-100 transition-colors"
                    >
                      Revoke
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
