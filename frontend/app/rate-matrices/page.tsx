'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Scale, RefreshCw } from 'lucide-react';
import { RateMatricesTabType } from '@/components/rate-matrices/rate-matrix-types';
import { MOCK_RATE_MATRICES } from '@/components/rate-matrices/rate-matrix-data';

export default function RateMatricesPage() {
  const [activeTab, setActiveTab] = useState<RateMatricesTabType>('RATES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_RATE_MATRICES.filter(r => 
      !search || r.matrixId.toLowerCase().includes(search.toLowerCase()) || r.carrier.toLowerCase().includes(search.toLowerCase()) || r.serviceLevel.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="rate-matrices">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SHIPPING RATE MATRIX & CARRIER PRIORITY ENGINE"
          title="SHIPPING RATE"
          highlightTitle="MATRICES"
          description="Carrier shipping rate matrix, priority routing rules, fuel surcharge updates, zone tier pricing, and rate comparison."
          icon={Scale}
          statusBadge="● RATE MATRIX ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="RATE MATRICES" value={`${MOCK_RATE_MATRICES.length}`} subtext="ACTIVE PRIORITY MATRICES" accentColor="text-blue-400" />
          <AGMetricCard label="AVG RATE USD" value="$36.25" subtext="PRIORITY OVERNIGHT RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="FUEL SURCHARGE" value="6.5% SURCHARGE" subtext="CURRENT WEEKLY INDEX" accentColor="text-emerald-400" />
          <AGMetricCard label="ROUTING SLA" value="100% OPTIMAL" subtext="LEAST-COST CARRIER MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Matrix ID, Carrier, Service..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['RATES', 'PRIORITY_RULES', 'FUEL_SURCHARGES', 'ZONE_MAPS', 'COMPARISON', 'AUDIT'] as RateMatricesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'RATES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">MATRIX ID</th>
                  <th className="p-3">CARRIER</th>
                  <th className="p-3">SERVICE LEVEL</th>
                  <th className="p-3">ZONE</th>
                  <th className="p-3">WEIGHT TIER</th>
                  <th className="p-3">RATE (USD)</th>
                  <th className="p-3">PRIORITY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.matrixId}</td>
                    <td className="p-3 font-bold text-slate-200">{r.carrier}</td>
                    <td className="p-3 font-bold text-purple-400">{r.serviceLevel}</td>
                    <td className="p-3 text-slate-300">{r.zone}</td>
                    <td className="p-3 text-slate-400">{r.weightTier}</td>
                    <td className="p-3 font-bold text-emerald-400">{r.rateUSD}</td>
                    <td className="p-3 text-emerald-400 font-bold">#{r.priority}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'RATES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
