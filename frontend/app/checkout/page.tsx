'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShoppingBag, RefreshCw } from 'lucide-react';
import { CheckoutTabType } from '@/components/checkout/checkout-types';
import { MOCK_CHECKOUT_SESSIONS } from '@/components/checkout/checkout-data';

export default function CheckoutPage() {
  const [activeTab, setActiveTab] = useState<CheckoutTabType>('SESSIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_CHECKOUT_SESSIONS.filter(c => 
      !search || c.sessionId.toLowerCase().includes(search.toLowerCase()) || c.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="checkout">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AGENT CHECKOUT SESSION & 3DS ORCHESTRATION"
          title="CHECKOUT"
          highlightTitle="SESSIONS"
          description="Autonomous agent checkout session control, 3DS challenge orchestration, processor routing, and session recovery."
          icon={ShoppingBag}
          statusBadge="● CHECKOUT ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CHECKOUT SESSIONS" value={`${MOCK_CHECKOUT_SESSIONS.length}`} subtext="ACTIVE ORCHESTRATION" accentColor="text-blue-400" />
          <AGMetricCard label="3DS AUTH RATE" value="99.9%" subtext="FRICTIONLESS PASS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG SESSION TIME" value="180ms" subtext="SUB-SECOND CHECKOUT" accentColor="text-emerald-400" />
          <AGMetricCard label="SESSION RECOVERY" value="100%" subtext="ZERO DROPPED FLOWS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Session ID, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SESSIONS', 'ACTIVE', '3DS_CHALLENGE', 'COMPLETED', 'FAILED', 'ROUTING', 'AUDIT'] as CheckoutTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SESSIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SESSION ID</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">MERCHANT</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">3DS STATUS</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.sessionId}</td>
                    <td className="p-3 font-bold text-purple-400">{c.agentId}</td>
                    <td className="p-3 text-slate-200">{c.merchant}</td>
                    <td className="p-3 font-bold text-emerald-400">{c.amount}</td>
                    <td className="p-3 text-emerald-400 font-bold">{c.threeDsStatus}</td>
                    <td className="p-3 text-slate-400">{c.processor}</td>
                    <td className="p-3"><AGBadge status={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SESSIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
