'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import { Building2, Save, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

export function SettingsOrganization() {
  const [orgName, setOrgName] = useState('AGENTPAY LABS');
  const [billingEmail, setBillingEmail] = useState('billing@agentpay.io');

  return (
    <AGCard className="space-y-4 font-mono text-xs max-w-4xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-400" /> ORGANIZATION & SUBSCRIPTION PLAN
          </h3>
          <p className="text-[10px] text-slate-400">Enterprise tenant details and security posture parameters</p>
        </div>
        <AGBadge status="POLICY_SECURE" label="ZERO-TRUST TENANT" />
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
              Organization Name
            </label>
            <input
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
            />
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-bold">
              Billing Email
            </label>
            <input
              type="email"
              value={billingEmail}
              onChange={(e) => setBillingEmail(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[10px]">
          <div className="p-3 bg-slate-950 rounded-xl border border-white/[0.06] space-y-1">
            <span className="text-slate-400 block">Organization ID</span>
            <span className="font-bold text-blue-400">ORG-AGP-001</span>
          </div>

          <div className="p-3 bg-slate-950 rounded-xl border border-white/[0.06] space-y-1">
            <span className="text-slate-400 block">Subscription Plan</span>
            <span className="font-bold text-emerald-400">ENTERPRISE</span>
          </div>

          <div className="p-3 bg-slate-950 rounded-xl border border-white/[0.06] space-y-1">
            <span className="text-slate-400 block">Active Members</span>
            <span className="font-bold text-slate-200">128 Members</span>
          </div>

          <div className="p-3 bg-slate-950 rounded-xl border border-white/[0.06] space-y-1">
            <span className="text-slate-400 block">Default Environment</span>
            <span className="font-bold text-blue-400">PRODUCTION</span>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <AGButton variant="primary" size="md" icon={Save} onClick={() => alert('Organization details saved')}>
            SAVE ORGANIZATION
          </AGButton>
        </div>
      </div>
    </AGCard>
  );
}
