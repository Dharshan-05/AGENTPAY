'use client';

import { OrganizationMemberRecord, RoleRecord, AuditLogRecord } from './source-types';
import { X, ShieldCheck } from 'lucide-react';

interface SourceInspectorProps {
  memberItem: OrganizationMemberRecord | null;
  roleItem: RoleRecord | null;
  auditItem: AuditLogRecord | null;
  onClose: () => void;
}

export function SourceInspector({ memberItem, roleItem, auditItem, onClose }: SourceInspectorProps) {
  if (!memberItem && !roleItem && !auditItem) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end font-sans">
      <div className="w-full max-w-md bg-white h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">SOURCE INSPECTOR</span>
              <h2 className="text-lg font-bold text-slate-900">
                {memberItem?.name || roleItem?.name || auditItem?.event}
              </h2>
            </div>
            <button onClick={onClose} className="p-1 rounded hover:bg-slate-100 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          {memberItem && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between"><span className="text-slate-500">Member ID:</span><span className="font-bold text-slate-900">{memberItem.id}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Email:</span><span className="text-blue-600 font-bold">{memberItem.email}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Role:</span><span className="font-bold text-slate-800">{memberItem.role}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Status:</span><span className="font-bold text-emerald-600">{memberItem.status}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Last Active:</span><span className="text-slate-600">{memberItem.lastActive}</span></div>
            </div>
          )}

          {roleItem && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between"><span className="text-slate-500">Role ID:</span><span className="font-bold text-slate-900">{roleItem.id}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Members Assigned:</span><span className="font-bold text-blue-600">{roleItem.membersCount} Users</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Grants Count:</span><span className="font-bold text-emerald-600">{roleItem.permissionsCount} Permissions</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Type:</span><span className="font-bold text-slate-800">{roleItem.status}</span></div>
            </div>
          )}

          {auditItem && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
              <div className="flex justify-between"><span className="text-slate-500">Audit ID:</span><span className="font-bold text-slate-900">{auditItem.id}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Actor:</span><span className="font-bold text-blue-600">{auditItem.actor}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Target Resource:</span><span className="font-bold text-slate-800">{auditItem.resource}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">IP Address:</span><span className="font-bold text-emerald-600">{auditItem.ipAddress}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Timestamp:</span><span className="text-slate-600">{auditItem.timestamp}</span></div>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-xl text-xs hover:bg-slate-800 transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
