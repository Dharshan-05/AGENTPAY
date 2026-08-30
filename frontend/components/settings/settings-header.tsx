'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { SlidersHorizontal, Download, Save, ShieldCheck, Globe } from 'lucide-react';

interface SettingsHeaderProps {
  currentEnv: 'PRODUCTION' | 'SANDBOX';
  onEnvChange: (env: 'PRODUCTION' | 'SANDBOX') => void;
  onSave: () => void;
  onExport: () => void;
}

export function SettingsHeader({ currentEnv, onEnvChange, onSave, onExport }: SettingsHeaderProps) {
  return (
    <PageHeader
      eyebrow="ZERO-TRUST IDENTITY, ACCESS & SECURITY CONTROL PLANE"
      title="SETT"
      highlightTitle="INGS"
      description="Manage account credentials, MFA policies, active sessions, RBAC permissions, environments, and audit activity."
      icon={SlidersHorizontal}
      statusBadge={
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ● SECURITY POSTURE: HEALTHY (98/100)
        </span>
      }
      actions={
        <>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-xs text-slate-300">
            <span className="text-slate-400">ORG:</span>
            <span className="text-blue-400 font-bold">ORG-AGP-001</span>
          </div>

          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 font-mono text-xs">
            <button
              onClick={() => onEnvChange('PRODUCTION')}
              className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                currentEnv === 'PRODUCTION'
                  ? 'bg-blue-500 text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              PROD
            </button>
            <button
              onClick={() => onEnvChange('SANDBOX')}
              className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                currentEnv === 'SANDBOX'
                  ? 'bg-amber-500 text-white shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              SANDBOX
            </button>
          </div>

          <AGButton variant="secondary" size="md" icon={Download} onClick={onExport}>
            Export Audit
          </AGButton>

          <AGButton variant="primary" size="md" icon={Save} onClick={onSave}>
            SAVE CHANGES
          </AGButton>
        </>
      }
    />
  );
}
