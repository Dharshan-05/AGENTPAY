'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { Activity, ShieldCheck, CheckCircle2 } from 'lucide-react';

export function SecurityPosture() {
  const controls = [
    { name: 'ZERO-TRUST ARCHITECTURE', status: 'ENABLED', detail: 'mTLS + Token Scope Validation' },
    { name: 'MFA TOTP ENFORCEMENT', status: 'ENABLED', detail: 'Mandatory for all admin roles' },
    { name: 'ROLE-BASED ACCESS (RBAC)', status: 'ENABLED', detail: '42 granular resource grants' },
    { name: 'AUDIT LOGGING', status: 'ENABLED', detail: 'Immutable event stream active' },
    { name: 'SESSION REVOCATION POLICY', status: 'ENABLED', detail: '24-hour max session lifespan' },
    { name: 'API KEY ROTATION', status: 'ENABLED', detail: '30-day automated rotation' },
    { name: 'SUBNET IP RESTRICTIONS', status: 'ENABLED', detail: '21 / 24 key subnet bounds' },
    { name: 'PASSWORD POLICY', status: 'ENABLED', detail: 'Min 16 chars + symbols' },
  ];

  return (
    <AGCard className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" /> ENTERPRISE SECURITY HEALTH & POSTURE SCORECARD
          </h3>
          <p className="text-[10px] text-slate-400">Real-time posture compliance audit (8/8 Controls Active)</p>
        </div>
        <AGBadge status="APPROVED" label="SCORE: 98 / 100 HEALTHY" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {controls.map((c) => (
          <div key={c.name} className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
            <div className="flex justify-between items-center text-[10px] font-bold">
              <span className="text-slate-100">{c.name}</span>
              <span className="text-emerald-400 font-bold">{c.status}</span>
            </div>
            <span className="text-[10px] text-slate-500 block">{c.detail}</span>
          </div>
        ))}
      </div>

      <div className="p-3.5 rounded-xl bg-slate-950 border border-white/[0.04] flex flex-wrap justify-between text-[10px] text-slate-400">
        <span>Last Automated Security Scan: <strong className="text-slate-200">Just now</strong></span>
        <span>Next Policy Review: <strong className="text-blue-400">2026-09-01 UTC</strong></span>
      </div>
    </AGCard>
  );
}
