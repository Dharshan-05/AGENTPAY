'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { MapPin, RefreshCw, Plus } from 'lucide-react';
import { AddressesTabType } from '@/components/addresses/address-types';
import { MOCK_ADDRESSES } from '@/components/addresses/address-data';

export default function AddressesPage() {
  const [activeTab, setActiveTab] = useState<AddressesTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_ADDRESSES.filter(a => 
      !search || a.addressId.toLowerCase().includes(search.toLowerCase()) || a.entityName.toLowerCase().includes(search.toLowerCase()) || a.cityStateZip.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="addresses">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="VERIFIED ADDRESS & LOCATION PROFILING PLANE"
          title="VERIFIED"
          highlightTitle="ADDRESSES"
          description="Customer & merchant address verification, CASS/Loqate geo-validation, tax nexus location profiling, and shipping address risk scoring."
          icon={MapPin}
          statusBadge="● GEO-VALIDATION ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Address Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD ADDRESS</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL ADDRESSES" value={`${MOCK_ADDRESSES.length}`} subtext="PROFILED LOCATIONS" accentColor="text-blue-400" />
          <AGMetricCard label="VERIFIED PASS" value="100%" subtext="CASS/LOQATE VALIDATED" accentColor="text-emerald-400" />
          <AGMetricCard label="TAX NEXUS BINDING" value="VERIFIED" subtext="AUTOMATED JURISDICTION" accentColor="text-emerald-400" />
          <AGMetricCard label="RISK FLAGS" value="00" subtext="ZERO HIGH-RISK GEO STOPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Address ID, Entity, Location..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'GEO_VERIFICATION', 'CUSTOMER_LINKAGE', 'MERCHANT_LOCATIONS', 'RISK_PROFILING', 'AUDIT'] as AddressesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ADDRESS ID</th>
                  <th className="p-3">ENTITY NAME</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">STREET ADDRESS</th>
                  <th className="p-3">CITY, STATE, ZIP</th>
                  <th className="p-3">COUNTRY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.addressId}</td>
                    <td className="p-3 font-bold text-slate-200">{a.entityName}</td>
                    <td className="p-3 font-bold text-purple-400">{a.type}</td>
                    <td className="p-3 text-slate-300">{a.street}</td>
                    <td className="p-3 text-slate-300">{a.cityStateZip}</td>
                    <td className="p-3 text-slate-400">{a.country}</td>
                    <td className="p-3"><AGBadge status={a.verificationStatus} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'REGISTRY' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
