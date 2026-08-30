'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldCheck, RefreshCw, Plus } from 'lucide-react';
import { MandatesTabType } from '@/components/mandates/mandate-types';
import { MOCK_MANDATES } from '@/components/mandates/mandate-data';

export default function MandatesPage() {
  const [activeTab, setActiveTab] = useState<MandatesTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_MANDATES.filter(m => 
      !search || m.mandateId.toLowerCase().includes(search.toLowerCase()) || m.customer.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="mandates">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="RECURRING DEBIT AUTHORIZATION & MANDATE ENGINE"
          title="PAYMENT"
          highlightTitle="MANDATES"
          description="Direct debit mandate authorization, UPI e-Mandates, ACH/SEPA standing orders, revocation management, and bank verification."
          icon={ShieldCheck}
          statusBadge="● MANDATE VAULT ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Mandate Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> NEW MANDATE</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE MANDATES" value={`${MOCK_MANDATES.length}`} subtext="AUTHORIZED STANDING ORDERS" accentColor="text-blue-400" />
          <AGMetricCard label="MAX DEBIT CAPACITY" value="$50,000.00" subtext="AUTHORIZATION LIMIT" accentColor="text-emerald-400" />
          <AGMetricCard label="VERIFIED BANKS" value="100%" subtext="HSM & mTLS BOUND" accentColor="text-emerald-400" />
          <AGMetricCard label="REVOCATIONS" value="00" subtext="ZERO MANDATE REVOKES" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Mandate ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'ACTIVE_MANDATES', 'ACH_SEPA', 'UPI_EMANDATE', 'REVOKED', 'VERIFICATION', 'AUDIT'] as MandatesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">MANDATE ID</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">MAX AMOUNT</th>
                  <th className="p-3">FREQUENCY</th>
                  <th className="p-3">BANK REFERENCE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(m => (
                  <tr key={m.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{m.mandateId}</td>
                    <td className="p-3 text-slate-200">{m.customer}</td>
                    <td className="p-3 font-bold text-purple-400">{m.mandateType}</td>
                    <td className="p-3 font-bold text-emerald-400">{m.maxAmount}</td>
                    <td className="p-3 text-slate-400">{m.frequency}</td>
                    <td className="p-3 text-slate-300">{m.bankRef}</td>
                    <td className="p-3"><AGBadge status={m.status} size="sm" /></td>
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
