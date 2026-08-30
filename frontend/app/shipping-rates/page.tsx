'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Scale, RefreshCw } from 'lucide-react';
import { ShippingRatesTabType } from '@/components/shipping-rates/shipping-rate-types';
import { MOCK_SHIPPING_RATES } from '@/components/shipping-rates/shipping-rate-data';

export default function ShippingRatesPage() {
  const [activeTab, setActiveTab] = useState<ShippingRatesTabType>('RATE_MATRIX');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SHIPPING_RATES.filter(r => 
      !search || r.rateId.toLowerCase().includes(search.toLowerCase()) || r.carrier.toLowerCase().includes(search.toLowerCase()) || r.service.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="shipping-rates">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SHIPPING RATE MATRIX & CARRIER COMPARISON PLANE"
          title="SHIPPING"
          highlightTitle="RATES"
          description="Real-time shipping rate calculation, carrier service comparison, fuel surcharge rules, and optimal routing logic."
          icon={Scale}
          statusBadge="● RATE CALCULATOR ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="RATE MATRICES" value={`${MOCK_SHIPPING_RATES.length}`} subtext="ACTIVE RATE CARDS" accentColor="text-blue-400" />
          <AGMetricCard label="AVG DISPATCH COST" value="$55.00" subtext="OPTIMIZED CARRIER RATES" accentColor="text-emerald-400" />
          <AGMetricCard label="CARRIER SERVICES" value="06 Services" subtext="GLOBAL DISPATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="ROUTING SAVINGS" value="14.2%" subtext="DYNAMIC CARRIER SELECTION" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Rate ID, Carrier, Service..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['RATE_MATRIX', 'CARRIERS', 'ROUTING_RULES', 'FUEL_SURCHARGES', 'DELIVERY_ESTIMATES', 'COMPARISON', 'AUDIT'] as ShippingRatesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'RATE_MATRIX' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RATE ID</th>
                  <th className="p-3">CARRIER</th>
                  <th className="p-3">SERVICE</th>
                  <th className="p-3">ORIGIN</th>
                  <th className="p-3">DESTINATION</th>
                  <th className="p-3">BASE RATE</th>
                  <th className="p-3">DELIVERY EST</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.rateId}</td>
                    <td className="p-3 font-bold text-slate-200">{r.carrier}</td>
                    <td className="p-3 font-bold text-purple-400">{r.service}</td>
                    <td className="p-3 text-slate-300">{r.originRegion}</td>
                    <td className="p-3 text-slate-300">{r.destRegion}</td>
                    <td className="p-3 font-bold text-emerald-400">{r.baseRate}</td>
                    <td className="p-3 text-slate-400">{r.deliveryEst}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'RATE_MATRIX' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
