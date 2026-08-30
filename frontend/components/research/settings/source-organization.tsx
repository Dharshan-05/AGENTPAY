'use client';

import { Building2, ShieldCheck, Check } from 'lucide-react';
import { useState } from 'react';

export function SourceOrganization() {
  const [orgName, setOrgName] = useState('AGENTPAY LABS');

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            Organization & Workspace Details
          </h3>
          <p className="text-xs text-slate-500">Excavated enterprise organization settings panel</p>
        </div>
      </div>

      <div className="space-y-4 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block font-bold text-slate-700 mb-1">Organization Name</label>
            <input
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">Organization ID</label>
            <div className="px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl font-mono font-bold text-slate-700">
              ORG-AGP-001
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 font-mono">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block">Subscription Plan</span>
            <span className="text-sm font-bold text-blue-700">ENTERPRISE</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block">Total Members</span>
            <span className="text-sm font-bold text-slate-900">128 Members</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block">Security Policy</span>
            <span className="text-sm font-bold text-emerald-600">ZERO-TRUST</span>
          </div>
        </div>
      </div>
    </div>
  );
}
