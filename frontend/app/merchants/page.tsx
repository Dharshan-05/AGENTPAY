'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { Building2, RefreshCw, Download, Plus, ArrowRight } from 'lucide-react';
import { MerchantTabType, MerchantRecord } from '@/components/merchants/merchant-types';
import { MOCK_MERCHANTS } from '@/components/merchants/merchant-data';

export default function MerchantsPage() {
  const [activeTab, setActiveTab] = useState<MerchantTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedMer, setSelectedMer] = useState<MerchantRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_MERCHANTS.filter(m => 
      !search || m.merchantId.toLowerCase().includes(search.toLowerCase()) || m.businessName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="merchants">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MERCHANT & SETTLEMENT CONTROL PLANE"
          title="MERCHANT"
          highlightTitle="OPERATIONS"
          description="Merchant entity onboarding, multi-connector processor binding, settlement currency configuration, and merchant risk monitoring."
          icon={Building2}
          statusBadge="● MERCHANT ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Merchant Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD MERCHANT</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="MERCHANTS" value={`${MOCK_MERCHANTS.length}`} subtext="ONBOARDED MERCHANTS" accentColor="text-blue-400" />
          <AGMetricCard label="ACTIVE MERCHANTS" value="03" subtext="PROCESSING LIVE" accentColor="text-emerald-400" />
          <AGMetricCard label="TOTAL SETTLED" value="$2.58M" subtext="CUMULATIVE VOLUME" accentColor="text-emerald-400" />
          <AGMetricCard label="CONNECTED PROCESSORS" value="04" subtext="STRIPE / ADYEN / JPM" accentColor="text-purple-400" />
          <AGMetricCard label="SUSPENDED MERCHANTS" value="01" subtext="RISK / COMPLIANCE STOP" accentColor="text-rose-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Merchant ID, Business Name, Processor..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'PROFILES', 'ACCOUNTS', 'PAYMENT_METHODS', 'PROCESSORS', 'RISK', 'SETTLEMENTS', 'AUDIT'] as MerchantTabType[]).map(t => (
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
                  <th className="p-3">MERCHANT ID</th>
                  <th className="p-3">BUSINESS NAME</th>
                  <th className="p-3">INDUSTRY</th>
                  <th className="p-3">COUNTRY / CURRENCY</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">VOLUME</th>
                  <th className="p-3">RISK TIER</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(m => (
                  <tr key={m.id} onClick={() => setSelectedMer(m)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{m.merchantId}</td>
                    <td className="p-3 font-bold text-slate-200">{m.businessName}</td>
                    <td className="p-3 text-slate-400">{m.industry}</td>
                    <td className="p-3 text-slate-300">{m.country} / {m.settlementCurrency}</td>
                    <td className="p-3 font-bold text-purple-400">{m.processor}</td>
                    <td className="p-3 font-bold text-emerald-400">{m.volume}</td>
                    <td className="p-3 font-bold"><span className={m.riskTier === 'LOW' ? 'text-emerald-400' : 'text-rose-400'}>{m.riskTier}</span></td>
                    <td className="p-3"><AGBadge status={m.accountStatus} size="sm" /></td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 4 MERCHANTS MONITORED
          </div>
        )}

        {selectedMer && (
          <AGDrawer isOpen={!!selectedMer} onClose={() => setSelectedMer(null)} title={`MERCHANT INSPECTOR: ${selectedMer.merchantId}`} subtitle="MERCHANT CONTROL PLANE">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-1">
                <div className="text-[9px] text-blue-400 font-bold uppercase">PROCESSOR BINDING</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedMer.merchantId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedMer.processor}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedMer.settlementCurrency}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Business:</span><span className="text-slate-200 font-bold">{selectedMer.businessName}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Industry:</span><span className="text-slate-300">{selectedMer.industry}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Volume:</span><span className="text-emerald-400 font-bold">{selectedMer.volume}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Last Settlement:</span><span className="text-slate-400">{selectedMer.lastSettlement}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
