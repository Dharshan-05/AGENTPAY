'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Building2, RefreshCw } from 'lucide-react';
import { SubMerchantsTabType } from '@/components/sub-merchants/sub-merchant-types';
import { MOCK_SUB_MERCHANTS } from '@/components/sub-merchants/sub-merchant-data';

export default function SubMerchantsPage() {
  const [activeTab, setActiveTab] = useState<SubMerchantsTabType>('MERCHANTS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SUB_MERCHANTS.filter(s => 
      !search || s.subMerchantId.toLowerCase().includes(search.toLowerCase()) || s.businessName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="sub-merchants">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MARKETPLACE SUB-MERCHANT & KYC/KYB ONBOARDING PLANE"
          title="SUB-MERCHANT"
          highlightTitle="OPERATIONS"
          description="Sub-merchant onboarding control plane, automated KYC/KYB verification, processing volume limits, and split account management."
          icon={Building2}
          statusBadge="● SUB-MERCHANT ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SUB-MERCHANTS" value={`${MOCK_SUB_MERCHANTS.length}`} subtext="ONBOARDED ENTITIES" accentColor="text-blue-400" />
          <AGMetricCard label="KYC / KYB PASS RATE" value="100% VERIFIED" subtext="FULLY COMPLIANT" accentColor="text-emerald-400" />
          <AGMetricCard label="MONTHLY CAPACITY" value="$1.25M" subtext="COMBINED PROCESSING LIMIT" accentColor="text-emerald-400" />
          <AGMetricCard label="ACCOUNT CONNECTIVITY" value="CUSTOM EXPRESS" subtext="DIRECT SPLIT ACCOUNT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Sub-Merchant ID, Business..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['MERCHANTS', 'KYC_KYB_VERIFICATION', 'SPLIT_ACCOUNTS', 'PROCESSING_LIMITS', 'AUDIT'] as SubMerchantsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'MERCHANTS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SUB-MERCHANT ID</th>
                  <th className="p-3">BUSINESS NAME</th>
                  <th className="p-3">JURISDICTION</th>
                  <th className="p-3">KYC / KYB STATUS</th>
                  <th className="p-3">MONTHLY LIMIT</th>
                  <th className="p-3">ACCOUNT TYPE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.subMerchantId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.businessName}</td>
                    <td className="p-3 text-slate-300">{s.jurisdiction}</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.kycKybStatus}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.monthlyVolumeLimit}</td>
                    <td className="p-3 text-purple-400 font-mono">{s.connectedAccountType}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'MERCHANTS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
