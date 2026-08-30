'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Network, RefreshCw } from 'lucide-react';
import { GatewayCascadingRulesTabType } from '@/components/gateway-cascading-rules/gateway-cascading-rule-types';
import { MOCK_GATEWAY_CASCADING_RULES } from '@/components/gateway-cascading-rules/gateway-cascading-rule-data';

export default function GatewayCascadingRulesPage() {
  const [activeTab, setActiveTab] = useState<GatewayCascadingRulesTabType>('CASCADING_RULES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_GATEWAY_CASCADING_RULES.filter(c => 
      !search || c.cascadingId.toLowerCase().includes(search.toLowerCase()) || c.ruleName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="gateway-cascading-rules">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SMART GATEWAY CASCADING & FAILOVER OPTIMIZER PLANE"
          title="GATEWAY CASCADING"
          highlightTitle="RULES"
          description="Autonomous PSP cascading failover, instant authorization recovery, latency SLA routing, and zero-decline optimization."
          icon={Network}
          statusBadge="● CASCADING ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="CASCADING RULES" value={`${MOCK_GATEWAY_CASCADING_RULES.length}`} subtext="ACTIVE FAILOVER RULES" accentColor="text-blue-400" />
          <AGMetricCard label="RECOVERY RATE" value="99.94%" subtext="AUTHORIZATION RECOVERY" accentColor="text-emerald-400" />
          <AGMetricCard label="FAILOVER LATENCY" value="< 45ms" subtext="INSTANT PSP SWITCH" accentColor="text-emerald-400" />
          <AGMetricCard label="DECLINE PREVENTION" value="+ 4.2% AUTH" subtext="NET AUTHORIZATION LIFT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Cascading ID, Rule Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CASCADING_RULES', 'FAILOVER_STRATEGIES', 'PSP_LATENCY_MATRIX', 'AUDIT'] as GatewayCascadingRulesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CASCADING_RULES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">CASCADING ID</th>
                  <th className="p-3">RULE NAME</th>
                  <th className="p-3">PRIMARY PSP</th>
                  <th className="p-3">FALLBACK PSP</th>
                  <th className="p-3">MAX RETRIES</th>
                  <th className="p-3">FAILOVER SLA</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.cascadingId}</td>
                    <td className="p-3 font-bold text-slate-200">{c.ruleName}</td>
                    <td className="p-3 font-bold text-emerald-400 font-mono">{c.primaryPsp}</td>
                    <td className="p-3 text-amber-400 font-mono font-bold">{c.fallbackPsp}</td>
                    <td className="p-3 text-slate-300 font-mono">{c.maxRetries} retries</td>
                    <td className="p-3 text-emerald-400 font-mono">{c.failoverLatencySlaMs} ms</td>
                    <td className="p-3"><AGBadge status={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CASCADING_RULES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
