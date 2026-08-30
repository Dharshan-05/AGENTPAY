'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Repeat, RefreshCw } from 'lucide-react';
import { ExchangesTabType } from '@/components/exchanges/exchange-types';
import { MOCK_EXCHANGES } from '@/components/exchanges/exchange-data';

export default function ExchangesPage() {
  const [activeTab, setActiveTab] = useState<ExchangesTabType>('EXCHANGES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_EXCHANGES.filter(e => 
      !search || e.exchangeId.toLowerCase().includes(search.toLowerCase()) || e.orderId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="exchanges">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ITEM EXCHANGE & PRICE VARIANCE RECONCILIATION"
          title="ITEM"
          highlightTitle="EXCHANGES"
          description="SKU swap processing, price variance calculation, automated payment difference collection, and inventory replacement."
          icon={Repeat}
          statusBadge="● EXCHANGE SWAP ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TOTAL EXCHANGES" value={`${MOCK_EXCHANGES.length}`} subtext="PROCESSED ITEM SWAPS" accentColor="text-blue-400" />
          <AGMetricCard label="EVEN EXCHANGES" value="50%" subtext="ZERO VARIANCE MATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="VARIANCE REVENUE" value="+$499.00" subtext="UPGRADE DIFFERENCE" accentColor="text-emerald-400" />
          <AGMetricCard label="SWAP SLA" value="100%" subtext="SAME-DAY REPLACEMENT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Exchange ID, Order ID..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['EXCHANGES', 'SKU_SWAPS', 'PRICE_VARIANCE', 'SHIPPING', 'COMPLETED', 'AUDIT'] as ExchangesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'EXCHANGES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">EXCHANGE ID</th>
                  <th className="p-3">ORDER ID</th>
                  <th className="p-3">ORIGINAL SKU</th>
                  <th className="p-3">NEW SKU</th>
                  <th className="p-3">PRICE VARIANCE</th>
                  <th className="p-3">VARIANCE STATUS</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(e => (
                  <tr key={e.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{e.exchangeId}</td>
                    <td className="p-3 font-bold text-purple-400">{e.orderId}</td>
                    <td className="p-3 text-slate-300">{e.originalSku}</td>
                    <td className="p-3 font-bold text-slate-200">{e.newSku}</td>
                    <td className="p-3 font-bold text-emerald-400">{e.priceVariance}</td>
                    <td className="p-3 text-amber-400 font-bold">{e.varianceStatus}</td>
                    <td className="p-3"><AGBadge status={e.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'EXCHANGES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
