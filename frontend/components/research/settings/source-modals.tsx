'use client';

import { X, UserPlus } from 'lucide-react';
import { useState } from 'react';

interface SourceModalsProps {
  isInviteOpen: boolean;
  onCloseInvite: () => void;
  onInviteMember: (email: string, role: string) => void;
}

export function SourceModals({ isInviteOpen, onCloseInvite, onInviteMember }: SourceModalsProps) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('SECURITY OPERATOR');

  if (!isInviteOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    onInviteMember(email, role);
    setEmail('');
    onCloseInvite();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 font-sans text-slate-800">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-base">Invite Organization Member</h3>
          </div>
          <button onClick={onCloseInvite} className="p-1 text-slate-400 hover:text-slate-600 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-sans">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. analyst@agentpay.io"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Role Assignment</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-medium focus:outline-none focus:border-blue-500"
            >
              <option value="SECURITY OPERATOR">SECURITY OPERATOR</option>
              <option value="DEVELOPER">DEVELOPER</option>
              <option value="ANALYST">ANALYST</option>
              <option value="VIEWER">VIEWER</option>
            </select>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2 font-semibold">
            <button
              type="button"
              onClick={onCloseInvite}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm transition-colors"
            >
              Send Invitation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
