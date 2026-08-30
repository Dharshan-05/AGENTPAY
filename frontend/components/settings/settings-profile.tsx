'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionUserProfile } from './settings-types';
import { User, Save, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface SettingsProfileProps {
  profile: ProductionUserProfile;
  onSaveProfile: (name: string, email: string) => void;
}

export function SettingsProfile({ profile, onSaveProfile }: SettingsProfileProps) {
  const [name, setName] = useState(profile.fullName);
  const [email, setEmail] = useState(profile.email);

  return (
    <AGCard className="space-y-4 font-mono text-xs max-w-4xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <User className="w-5 h-5 text-blue-400" /> ACCOUNT PROFILE & IDENTITY
          </h3>
          <p className="text-[10px] text-slate-400">Authenticated user identity and security credentials metadata</p>
        </div>
        <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5" /> ZERO-TRUST VERIFIED
        </span>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
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
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] text-[11px]">
          <div>
            <span className="text-slate-400 block text-[10px]">User ID:</span>
            <span className="font-bold text-blue-400">{profile.userId}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Assigned Role:</span>
            <span className="font-bold text-emerald-400">{profile.role}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Organization ID:</span>
            <span className="font-bold text-slate-200">{profile.organizationId}</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/40 border border-white/[0.04] space-y-1 text-[10px] text-slate-400">
          <div className="flex justify-between">
            <span>Last Login Authentication:</span>
            <span className="text-slate-300">{profile.lastLogin}</span>
          </div>
          <div className="flex justify-between">
            <span>Password Age / Rotation:</span>
            <span className="text-emerald-400 font-bold">{profile.passwordLastChanged}</span>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <AGButton variant="primary" size="md" icon={Save} onClick={() => onSaveProfile(name, email)}>
            SAVE PROFILE
          </AGButton>
        </div>
      </div>
    </AGCard>
  );
}
