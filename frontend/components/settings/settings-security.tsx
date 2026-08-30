'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ShieldCheck, Lock, Smartphone, Key, AlertOctagon } from 'lucide-react';
import { useState } from 'react';

export function SettingsSecurity() {
  const [mfaEnabled, setMfaEnabled] = useState(true);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const toggleMfa = () => {
    if (mfaEnabled) {
      setShowConfirmModal(true);
    } else {
      setMfaEnabled(true);
    }
  };

  const confirmDisableMfa = () => {
    setMfaEnabled(false);
    setShowConfirmModal(false);
  };

  return (
    <div className="space-y-6 font-mono text-xs max-w-4xl">
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" /> MULTI-FACTOR AUTHENTICATION & SECURITY POLICIES
            </h3>
            <p className="text-[10px] text-slate-400">TOTP authenticator app and hardware security key policy enforcement</p>
          </div>
          <AGBadge status={mfaEnabled ? 'APPROVED' : 'REVIEW'} label={mfaEnabled ? '● MFA ACTIVE' : '● MFA DISABLED'} />
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-white/[0.08] flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-100 block">Hardware Security Key / TOTP Authenticator</span>
              <p className="text-[10px] text-slate-400">Require FIDO2 WebAuthn or TOTP code for administrative actions</p>
            </div>

            <AGButton variant={mfaEnabled ? 'danger' : 'primary'} size="sm" onClick={toggleMfa}>
              {mfaEnabled ? 'DISABLE MFA' : 'ENABLE MFA'}
            </AGButton>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[10px]">
            <div className="p-3 bg-slate-950/80 rounded-xl border border-white/[0.06] space-y-1">
              <span className="text-slate-400 uppercase font-bold block">Password Length</span>
              <span className="font-bold text-emerald-400">Min 16 Characters</span>
            </div>
            <div className="p-3 bg-slate-950/80 rounded-xl border border-white/[0.06] space-y-1">
              <span className="text-slate-400 uppercase font-bold block">Rotation Enforcement</span>
              <span className="font-bold text-blue-400">90 Days Mandatory</span>
            </div>
            <div className="p-3 bg-slate-950/80 rounded-xl border border-white/[0.06] space-y-1">
              <span className="text-slate-400 uppercase font-bold block">Session Lifespan</span>
              <span className="font-bold text-slate-200">24 Hours Max</span>
            </div>
            <div className="p-3 bg-slate-950/80 rounded-xl border border-white/[0.06] space-y-1">
              <span className="text-slate-400 uppercase font-bold block">Brute-Force Shield</span>
              <span className="font-bold text-emerald-400">Lock after 5 Attempts</span>
            </div>
          </div>
        </div>
      </AGCard>

      {/* CONFIRMATION MODAL FOR DISABLING MFA */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-red-500/30 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-red-400 font-bold text-sm">
              <AlertOctagon className="w-5 h-5" /> CONFIRM MFA DE-ACTIVATION
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              Disabling Multi-Factor Authentication will reduce your account security posture and trigger an immediate alert to AGENTGUARD. Are you sure?
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <AGButton variant="ghost" size="md" onClick={() => setShowConfirmModal(false)}>
                CANCEL
              </AGButton>
              <AGButton variant="danger" size="md" onClick={confirmDisableMfa}>
                CONFIRM DISABLE
              </AGButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
