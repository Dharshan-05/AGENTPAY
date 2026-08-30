'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Layers, RefreshCw, Plus } from 'lucide-react';
import { PlansTabType } from '@/components/plans/plan-types';
import { MOCK_PLANS } from '@/components/plans/plan-data';

export default function PlansPage() {
  const [activeTab, setActiveTab] = useState<PlansTabType>('PRICING_PLANS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PLANS.filter(p => 
      !search || p.planId.toLowerCase().includes(search.toLowerCase()) || p.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="plans">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PRICING & ENTITLEMENT GOVERNANCE PLANE"
          title="PRICING"
          highlightTitle="PLANS"
          description="Subscription pricing plans, metered usage tiers, agent execution limits, multi-currency pricing, and entitlement governance."
          icon={Layers}
          statusBadge="● PLAN CATALOG ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Plan Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> CREATE PLAN</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="PRICING PLANS" value={`${MOCK_PLANS.length}`} subtext="ACTIVE CATALOG PLANS" accentColor="text-blue-400" />
          <AGMetricCard label="ENTERPRISE TIER" value="$4,999/mo" subtext="TOP TIER CONTRACT" accentColor="text-emerald-400" />
          <AGMetricCard label="PRO TIER" value="$999/mo" subtext="GROWTH CONTRACT" accentColor="text-blue-400" />
          <AGMetricCard label="ENTITLEMENTS" value="ENFORCED" subtext="STRICT AGENT LIMITS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Plan ID, Plan Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['PRICING_PLANS', 'TIERS', 'USAGE_PRICING', 'LIMITS', 'ENTITLEMENTS', 'CURRENCIES', 'ARCHIVED', 'AUDIT'] as PlansTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'PRICING_PLANS' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map(p => (
              <div key={p.id} className="p-5 rounded-2xl bg-slate-900/60 border border-white/[0.08] space-y-3">
                <div className="flex justify-between items-center"><span className="text-[10px] text-purple-400 font-bold">{p.planId}</span><AGBadge status={p.status} size="sm" /></div>
                <h4 className="font-bold text-slate-100 text-base">{p.name}</h4>
                <div className="text-xl font-bold text-emerald-400">{p.monthlyPrice} <span className="text-xs text-slate-500">/ month</span></div>
                <div className="text-xs text-slate-400">Annual: {p.annualPrice} · Agent Limit: {p.agentLimit} agents</div>
              </div>
            ))}
          </div>
        )}
        {activeTab !== 'PRICING_PLANS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
