'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { Receipt, RefreshCw, Download, Plus, ArrowRight } from 'lucide-react';
import { PaymentIntentTabType, PaymentIntentRecord } from '@/components/payment-intents/payment-intent-types';
import { MOCK_INTENTS } from '@/components/payment-intents/payment-intent-data';

export default function PaymentIntentsPage() {
  const [activeTab, setActiveTab] = useState<PaymentIntentTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedPi, setSelectedPi] = useState<PaymentIntentRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_INTENTS.filter(i => 
      !search || i.intentId.toLowerCase().includes(search.toLowerCase()) || i.customer.toLowerCase().includes(search.toLowerCase()) || i.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payment-intents">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="INTENT & AUTHORIZATION CONTROL PLANE"
          title="PAYMENT INTENT"
          highlightTitle="OPERATIONS"
          description="Real-time payment intent lifecycle tracking, 3DS authentication state, processor authorization, and intent failure diagnostics."
          icon={Receipt}
          statusBadge="● INTENT ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Intent Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> CREATE INTENT</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="PAYMENT INTENTS" value={`${MOCK_INTENTS.length}`} subtext="TOTAL LIFECYCLE CHAINS" accentColor="text-blue-400" />
          <AGMetricCard label="SUCCEEDED" value="01" subtext="CAPTURED & SETTLED" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTHORIZED" value="01" subtext="FUNDS RESERVED" accentColor="text-blue-400" />
          <AGMetricCard label="PROCESSING" value="01" subtext="IN-FLIGHT CONNECTOR" accentColor="text-amber-400" />
          <AGMetricCard label="FAILED / DECLINED" value="01" subtext="RISK / 3DS STOPS" accentColor="text-rose-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Intent ID, Customer, Agent, Auth Code..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'INTENTS', 'AUTHORIZATION', 'PROCESSING', 'ROUTING', 'RISK', 'FAILURES', 'AUDIT'] as PaymentIntentTabType[]).map(t => (
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
                  <th className="p-3">INTENT ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">METHOD</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">AUTH CODE</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(i => (
                  <tr key={i.id} onClick={() => setSelectedPi(i)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-purple-400">{i.intentId}</td>
                    <td className="p-3 font-bold text-slate-100">{i.amount} ({i.currency})</td>
                    <td className="p-3 text-slate-300">{i.customer}</td>
                    <td className="p-3 font-bold text-blue-400">{i.agentId}</td>
                    <td className="p-3 text-slate-400">{i.paymentMethod}</td>
                    <td className="p-3"><AGBadge status={i.status} size="sm" /></td>
                    <td className="p-3 font-bold text-slate-300">{i.processor}</td>
                    <td className="p-3 font-mono text-[10px] text-emerald-400">{i.authCode}</td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 4 INTENT CHAINS MONITORED
          </div>
        )}

        {selectedPi && (
          <AGDrawer isOpen={!!selectedPi} onClose={() => setSelectedPi(null)} title={`INTENT INSPECTOR: ${selectedPi.intentId}`} subtitle="PAYMENT INTENT LIFECYCLE CONTROL">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-1">
                <div className="text-[9px] text-blue-400 font-bold uppercase">LIFECYCLE CHAIN</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedPi.agentId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedPi.intentId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedPi.status}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Amount:</span><span className="text-slate-100 font-bold">{selectedPi.amount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Processor:</span><span className="text-slate-300 font-bold">{selectedPi.processor}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Auth Code:</span><span className="text-emerald-400 font-bold">{selectedPi.authCode}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Risk Score:</span><span className="text-blue-400 font-bold">{selectedPi.riskScore}/100</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
