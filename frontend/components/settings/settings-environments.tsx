'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { ProductionEnvironmentRecord } from './settings-types';
import { Globe, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

interface SettingsEnvironmentsProps {
  environments: ProductionEnvironmentRecord[];
  currentEnv: 'PRODUCTION' | 'SANDBOX';
  onSwitchEnv: (env: 'PRODUCTION' | 'SANDBOX') => void;
}

export function SettingsEnvironments({
  environments,
  currentEnv,
  onSwitchEnv,
}: SettingsEnvironmentsProps) {
  const [confirmEnvSwitch, setConfirmEnvSwitch] = useState<'PRODUCTION' | 'SANDBOX' | null>(null);

  const handleEnvClick = (targetEnv: 'PRODUCTION' | 'SANDBOX') => {
    if (targetEnv === currentEnv) return;
    setConfirmEnvSwitch(targetEnv);
  };

  const confirmSwitch = () => {
    if (confirmEnvSwitch) {
      onSwitchEnv(confirmEnvSwitch);
      setConfirmEnvSwitch(null);
    }
  };

  return (
    <div className="space-y-6 font-mono text-xs max-w-4xl">
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-400" /> ENVIRONMENT CONFIGURATION & ISOLATION
            </h3>
            <p className="text-[10px] text-slate-400 font-normal">Strict boundary isolation between Live Production and Demo Sandbox</p>
          </div>
          <AGBadge status="APPROVED" label={`CURRENT: ${currentEnv}`} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {environments.map((env) => {
            const isSelected = currentEnv === env.name;
            return (
              <div
                key={env.id}
                className={`p-4 rounded-xl border space-y-3 transition-all ${
                  isSelected
                    ? 'bg-blue-500/10 border-blue-500/40 shadow-[0_0_20px_rgba(59,130,246,0.15)]'
                    : 'bg-slate-950/80 border-white/[0.06]'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-slate-100 text-sm">{env.name}</span>
                  <AGBadge status={env.name === 'PRODUCTION' ? 'APPROVED' : 'PENDING'} label={`● ${env.status}`} />
                </div>

                <div className="space-y-1.5 text-[10px]">
                  <span className="text-slate-400 font-bold uppercase block">Capabilities</span>
                  {env.capabilities.map((cap) => (
                    <div key={cap} className="flex items-center gap-1.5 text-slate-300">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{cap}</span>
                    </div>
                  ))}
                </div>

                <div className="pt-2">
                  <AGButton
                    variant={isSelected ? 'secondary' : 'primary'}
                    size="sm"
                    className="w-full justify-center"
                    onClick={() => handleEnvClick(env.name)}
                  >
                    {isSelected ? 'CURRENT ACTIVE' : `SWITCH TO ${env.name}`}
                  </AGButton>
                </div>
              </div>
            );
          })}
        </div>
      </AGCard>

      {/* SWITCH CONFIRMATION MODAL */}
      {confirmEnvSwitch && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-blue-500/30 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-blue-400 font-bold text-sm">
              <Globe className="w-5 h-5" /> CONFIRM ENVIRONMENT SWITCH
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              You are about to switch workspace context to <strong className="text-white">{confirmEnvSwitch}</strong>. This changes active telemetry streams and credential scopes. Proceed?
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <AGButton variant="ghost" size="md" onClick={() => setConfirmEnvSwitch(null)}>
                CANCEL
              </AGButton>
              <AGButton variant="primary" size="md" onClick={confirmSwitch}>
                CONFIRM SWITCH
              </AGButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
