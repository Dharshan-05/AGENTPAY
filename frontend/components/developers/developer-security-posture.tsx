'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldCheck, Lock, Key, Server } from 'lucide-react';

export function DeveloperSecurityPosture() {
  return (
    <div className="space-y-6 font-mono text-xs">
      <AGCard className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> DEVELOPER SECURITY POSTURE & GOVERNANCE
            </h3>
            <p className="text-[10px] text-slate-400">Zero-Trust developer access controls, token rotation enforcement, and mTLS security status</p>
          </div>
          <AGBadge status="POLICY_SECURE" label="ZERO-TRUST ENFORCED" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">API KEY ROTATION</span>
            <div className="text-lg font-bold text-emerald-400">98.4% COMPLIANT</div>
            <span className="text-[10px] text-slate-500">Enforced 30-day rotation</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">IP RESTRICTIONS</span>
            <div className="text-lg font-bold text-blue-400">21 / 24 KEYS</div>
            <span className="text-[10px] text-slate-500">Subnet binding active</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">mTLS AUTHENTICATION</span>
            <div className="text-lg font-bold text-emerald-400">ENFORCED</div>
            <span className="text-[10px] text-slate-500">Client cert validation</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">WEBHOOK SIGNATURES</span>
            <div className="text-lg font-bold text-emerald-400">100% VERIFIED</div>
            <span className="text-[10px] text-slate-500">HMAC SHA-256 Digest</span>
          </div>
        </div>
      </AGCard>
    </div>
  );
}
