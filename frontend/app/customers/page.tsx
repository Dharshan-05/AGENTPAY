'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { Users, RefreshCw, Download, UserPlus, ArrowRight, ShieldCheck, CreditCard, Activity } from 'lucide-react';
import { CustomerTabType, CustomerRecord } from '@/components/customers/customer-types';
import { MOCK_CUSTOMERS } from '@/components/customers/customer-data';

export default function CustomersPage() {
  const [activeTab, setActiveTab] = useState<CustomerTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedCus, setSelectedCus] = useState<CustomerRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_CUSTOMERS.filter(c => 
      !search || c.customerId.toLowerCase().includes(search.toLowerCase()) || c.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="customers">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="IDENTITY & ENTITY CONTROL PLANE"
          title="CUSTOMER"
          highlightTitle="OPERATIONS"
          description="Autonomous agent identity governance, customer entity profiling, linked payment instruments, and FraudGuard entity risk tracking."
          icon={Users}
          statusBadge="● CUSTOMER ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Customer Flow')}><UserPlus className="w-3.5 h-3.5 mr-1.5" /> ADD CUSTOMER</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="TOTAL CUSTOMERS" value={`${MOCK_CUSTOMERS.length}`} subtext="REGISTERED ENTITIES" accentColor="text-blue-400" />
          <AGMetricCard label="ACTIVE ENTITIES" value="04" subtext="VERIFIED & ROUTING" accentColor="text-emerald-400" />
          <AGMetricCard label="TOTAL VOLUME" value="$1.58M" subtext="ALL-TIME PROCESSED" accentColor="text-emerald-400" />
          <AGMetricCard label="KYC PENDING" value="01" subtext="IDENTITY VERIFICATION" accentColor="text-amber-400" />
          <AGMetricCard label="FLAGGED RISK" value="01" subtext="ELEVATED FRAUD SCORE" accentColor="text-rose-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Customer ID, Name, Email, Agent..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'PROFILES', 'IDENTITY', 'AGENTS', 'PAYMENT_METHODS', 'RISK', 'ACTIVITY', 'AUDIT'] as CustomerTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">CUSTOMER ID</th>
                  <th className="p-3">NAME &amp; EMAIL</th>
                  <th className="p-3">COUNTRY / CURRENCY</th>
                  <th className="p-3">VERIFICATION</th>
                  <th className="p-3">LINKED AGENT</th>
                  <th className="p-3">PAYMENT METHOD</th>
                  <th className="p-3">RISK SCORE</th>
                  <th className="p-3">PROCESSED VOLUME</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} onClick={() => setSelectedCus(c)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.customerId}</td>
                    <td className="p-3"><div className="font-bold text-slate-200">{c.name}</div><div className="text-[10px] text-slate-500">{c.emailMasked}</div></td>
                    <td className="p-3 text-slate-300">{c.country} / {c.currency}</td>
                    <td className="p-3"><AGBadge status={c.verificationState} size="sm" /></td>
                    <td className="p-3 font-bold text-purple-400">{c.linkedAgentId}</td>
                    <td className="p-3 text-emerald-400">{c.paymentMethod}</td>
                    <td className="p-3 font-bold"><span className={c.riskScore < 30 ? 'text-emerald-400' : 'text-rose-400'}>{c.riskScore}/100</span></td>
                    <td className="p-3 font-bold text-slate-200">{c.totalVolume}</td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 5 RECORDS MONITORED
          </div>
        )}

        {selectedCus && (
          <AGDrawer isOpen={!!selectedCus} onClose={() => setSelectedCus(null)} title={`CUSTOMER INSPECTOR: ${selectedCus.customerId}`} subtitle="CUSTOMER IDENTITY & RISK CONTROL">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-1">
                <div className="text-[9px] text-blue-400 font-bold uppercase">CAUSAL TRACE</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedCus.customerId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedCus.linkedAgentId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedCus.paymentMethod}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Name:</span><span className="text-slate-200 font-bold">{selectedCus.name}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Verification:</span><span className="text-emerald-400 font-bold">{selectedCus.verificationState}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Volume:</span><span className="text-slate-200 font-bold">{selectedCus.totalVolume}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Risk Score:</span><span className="text-rose-400 font-bold">{selectedCus.riskScore}/100 ({selectedCus.riskTier})</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
