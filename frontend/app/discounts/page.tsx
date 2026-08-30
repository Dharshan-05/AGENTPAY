'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Tag, RefreshCw, Plus } from 'lucide-react';
import { DiscountsTabType } from '@/components/discounts/discount-types';
import { MOCK_DISCOUNTS } from '@/components/discounts/discount-data';

export default function DiscountsPage() {
  const [activeTab, setActiveTab] = useState<DiscountsTabType>('RULES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_DISCOUNTS.filter(d => 
      !search || d.discountId.toLowerCase().includes(search.toLowerCase()) || d.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="discounts">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="DISCOUNT & PROMOTION ENGINE CONTROL PLANE"
          title="DISCOUNT"
          highlightTitle="RULES"
          description="Automatic volume discount engine, product-level price reductions, tiered promotional rules, and order allocation."
          icon={Tag}
          statusBadge="● PROMOTION ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Discount Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD DISCOUNT</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="DISCOUNT RULES" value={`${MOCK_DISCOUNTS.length}`} subtext="ACTIVE ENGINE RULES" accentColor="text-blue-400" />
          <AGMetricCard label="APPLIED SAVINGS 24H" value="$14,290.00" subtext="TOTAL PROMO VALUE" accentColor="text-emerald-400" />
          <AGMetricCard label="TOTAL REDEMPTIONS" value="230" subtext="PROMOTION REDEMPTIONS" accentColor="text-emerald-400" />
          <AGMetricCard label="RULE ACCURACY" value="100%" subtext="ZERO CONFLICT STOPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Discount ID, Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['RULES', 'AUTOMATIC', 'TIERED', 'PROMOTIONS', 'EXCLUSIONS', 'APPLICATIONS', 'AUDIT'] as DiscountsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'RULES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">DISCOUNT ID</th>
                  <th className="p-3">RULE NAME</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">VALUE</th>
                  <th className="p-3">ALLOCATION</th>
                  <th className="p-3">USAGES</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{d.discountId}</td>
                    <td className="p-3 font-bold text-slate-200">{d.name}</td>
                    <td className="p-3 font-bold text-purple-400">{d.type}</td>
                    <td className="p-3 font-bold text-emerald-400">{d.value}</td>
                    <td className="p-3 text-slate-300">{d.allocation}</td>
                    <td className="p-3 text-slate-400">{d.usageCount} uses</td>
                    <td className="p-3"><AGBadge status={d.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'RULES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
