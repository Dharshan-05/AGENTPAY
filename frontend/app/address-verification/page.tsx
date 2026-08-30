'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { MapPin, RefreshCw } from 'lucide-react';
import { AddressVerificationTabType } from '@/components/address-verification/address-verification-types';
import { MOCK_ADDRESS_VERIFICATION } from '@/components/address-verification/address-verification-data';

export default function AddressVerificationPage() {
  const [activeTab, setActiveTab] = useState<AddressVerificationTabType>('VERIFICATIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ADDRESS_VERIFICATION.filter(a => 
      !search || a.addressId.toLowerCase().includes(search.toLowerCase()) || a.customerRef.toLowerCase().includes(search.toLowerCase()) || a.cityState.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="address-verification">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ADDRESS VERIFICATION & CASS GEO-RISK PLANE"
          title="ADDRESS"
          highlightTitle="VERIFICATION"
          description="CASS & Loqate address standardization, AVS zip code match, geo-risk score calculation, and tax nexus location binding."
          icon={MapPin}
          statusBadge="● CASS VERIFICATION ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="VERIFIED ADDRESSES" value={`${MOCK_ADDRESS_VERIFICATION.length}`} subtext="CASS STANDARDIZED" accentColor="text-blue-400" />
          <AGMetricCard label="CASS ACCURACY" value="100% MATCH" subtext="ZIP+4 STANDARDIZATION" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG GEO RISK" value="6 / 100" subtext="LOW GEO-LOCATION RISK" accentColor="text-emerald-400" />
          <AGMetricCard label="TAX NEXUS BIND" value="VERIFIED" subtext="AUTOMATED NEXUS MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Address ID, Customer, City/State..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['VERIFICATIONS', 'GEO_RISK', 'TAX_NEXUS', 'CASS_STANDARDS', 'RISK_SIGNALS', 'AUDIT'] as AddressVerificationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'VERIFICATIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ADDRESS ID</th>
                  <th className="p-3">CUSTOMER REF</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">CITY / STATE</th>
                  <th className="p-3">POSTAL CODE</th>
                  <th className="p-3">VERIFICATION</th>
                  <th className="p-3">GEO RISK</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.addressId}</td>
                    <td className="p-3 font-bold text-purple-400">{a.customerRef}</td>
                    <td className="p-3 text-slate-200">{a.type}</td>
                    <td className="p-3 font-bold text-slate-300">{a.cityState}</td>
                    <td className="p-3 font-mono text-slate-400">{a.postalCode}</td>
                    <td className="p-3 text-emerald-400 font-bold">{a.verificationStatus}</td>
                    <td className="p-3 text-emerald-400 font-bold">{a.geoRiskScore} / 100</td>
                    <td className="p-3"><AGBadge status={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'VERIFICATIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
