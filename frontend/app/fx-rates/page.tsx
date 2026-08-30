'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { RefreshCw, Coins } from 'lucide-react';
import { FxTabType } from '@/components/fx-rates/fx-rate-types';
import { MOCK_FX_RATES } from '@/components/fx-rates/fx-rate-data';

export default function FxRatesPage() {
  const [activeTab, setActiveTab] = useState<FxTabType>('LIVE_RATES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_FX_RATES.filter(f => 
      !search || f.fxId.toLowerCase().includes(search.toLowerCase()) || f.pair.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="fx-rates">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="FOREIGN EXCHANGE & TREASURY CONVERSION PLANE"
          title="FOREIGN"
          highlightTitle="EXCHANGE (FX)"
          description="Real-time FX currency conversion rates, multi-currency treasury hedging, dynamic spread calculations, and cross-border settlement."
          icon={Coins}
          statusBadge="● FX FEED LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="FX CURRENCY PAIRS" value={`${MOCK_FX_RATES.length}`} subtext="ACTIVE LIVE FEEDS" accentColor="text-blue-400" />
          <AGMetricCard label="EUR / USD RATE" value="1.0850" subtext="SPREAD 0.0002" accentColor="text-emerald-400" />
          <AGMetricCard label="USD / INR RATE" value="83.9200" subtext="SPREAD 0.0050" accentColor="text-emerald-400" />
          <AGMetricCard label="24H FX VOLUME" value="$8.92M" subtext="CROSS-BORDER SETTLED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search FX ID, Currency Pair..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['LIVE_RATES', 'CONVERSIONS', 'TREASURY_HEDGING', 'SPREADS', 'PAIRS', 'HISTORICAL', 'AUDIT'] as FxTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'LIVE_RATES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">FX ID</th>
                  <th className="p-3">CURRENCY PAIR</th>
                  <th className="p-3">SPOT RATE</th>
                  <th className="p-3">SPREAD</th>
                  <th className="p-3">24H VOLUME</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(f => (
                  <tr key={f.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{f.fxId}</td>
                    <td className="p-3 font-bold text-purple-400">{f.pair}</td>
                    <td className="p-3 font-bold text-emerald-400">{f.rate}</td>
                    <td className="p-3 text-slate-300">{f.spread}</td>
                    <td className="p-3 text-slate-200">{f.volume24h}</td>
                    <td className="p-3"><AGBadge status={f.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'LIVE_RATES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
