'use client';

import { ShieldCheck, Lock, Smartphone, Key } from 'lucide-react';
import { useState } from 'react';

export function SourceSecurity() {
  const [mfaEnabled, setMfaEnabled] = useState(true);

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Security, Authentication & MFA
          </h3>
          <p className="text-xs text-slate-500">Excavated security administration settings panel</p>
        </div>
        <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold rounded-full">
          SECURITY POSTURE ACTIVE
        </span>
      </div>

      <div className="space-y-4 text-xs">
        {/* MFA STATUS TOGGLE */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
          <div>
            <span className="font-bold text-slate-900 block">Two-Factor Authentication (MFA / TOTP)</span>
            <span className="text-slate-500 text-[11px]">Enforce hardware security key or authenticator app for login authorization</span>
          </div>

          <button
            onClick={() => setMfaEnabled(!mfaEnabled)}
            className={`px-3 py-1.5 rounded-xl font-bold text-xs transition-colors ${
              mfaEnabled ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
            }`}
          >
            {mfaEnabled ? 'MFA ENABLED' : 'ENABLE MFA'}
          </button>
        </div>

        {/* PASSWORD POLICY */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-bold text-slate-900">Password Policy & Rotation</span>
            <span className="text-slate-500 font-mono text-[11px]">Last changed: 14 days ago</span>
          </div>
          <p className="text-slate-500 text-[11px]">
            Password requires min 16 characters, uppercase, numbers, and special symbols. 90-day rotation enforced.
          </p>
        </div>
      </div>
    </div>
  );
}
