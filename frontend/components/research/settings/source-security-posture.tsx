'use client';

import { Activity, ShieldCheck, CheckCircle2 } from 'lucide-react';

export function SourceSecurityPosture() {
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
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            Security Health & Posture Scorecard
          </h3>
          <p className="text-xs text-slate-500">Excavated enterprise security posture dashboard (8/8 Controls Active)</p>
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-full">
          100% HEALTHY (8/8 ACTIVE)
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-xs">
        {controls.map((c) => (
          <div key={c.name} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
            <div className="flex justify-between items-center text-[10px] font-bold">
              <span className="text-slate-900 font-sans">{c.name}</span>
              <span className="text-emerald-700 font-bold">{c.status}</span>
            </div>
            <span className="text-[10px] text-slate-500 block">{c.detail}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
