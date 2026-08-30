'use client';

import { AGModal } from '@/components/ui/ag-modal';
import { AGButton } from '@/components/ui/ag-button';
import { UserPlus, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInvite: (name: string, email: string, role: string) => void;
}

export function InviteMemberModal({ isOpen, onClose, onInvite }: InviteMemberModalProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('SECURITY OPERATOR');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) return;
    onInvite(name, email, role);
    setName('');
    setEmail('');
    onClose();
  };

  return (
    <AGModal
      isOpen={isOpen}
      onClose={onClose}
      title="INVITE ORGANIZATION MEMBER"
      subtitle="ZERO-TRUST GOVERNED TEAM MEMBER INVITATION"
    >
      <form onSubmit={handleSubmit} className="space-y-4 font-mono text-xs">
        <div>
          <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
            Member Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Sarah Jenkins"
            className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
            required
          />
        </div>

        <div>
          <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="e.g. sjenkins@agentpay.io"
            className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
            required
          />
        </div>

        <div>
          <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
            Role Assignment
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
          >
            <option value="SECURITY OPERATOR">SECURITY OPERATOR</option>
            <option value="DEVELOPER">DEVELOPER</option>
            <option value="ANALYST">ANALYST</option>
          </select>
        </div>

        <div className="pt-2 flex items-center justify-end gap-2">
          <AGButton variant="ghost" size="md" onClick={onClose} type="button">
            CANCEL
          </AGButton>
          <AGButton variant="primary" size="md" type="submit">
            SEND INVITATION
          </AGButton>
        </div>
      </form>
    </AGModal>
  );
}
