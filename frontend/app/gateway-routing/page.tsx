'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Network, RefreshCw } from 'lucide-react';
import { GatewayRoutingTabType } from '@/components/gateway-routing/gateway-routing-types';
import { MOCK_GATEWAY_ROUTING } from '@/components/gateway-routing/gateway-routing-data';

export default function GatewayRoutingPage() {
  const [activeTab, setActiveTab] = useState<GatewayRoutingTabType>('ROUTING_RULES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_GATEWAY_ROUTING.filter(g => 
      !search || g.ruleId.toLowerCase().includes(search.toLowerCase()) || g.ruleName.toLowerCase().includes(search.toLowerCase()) || g.primaryGateway.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="gateway-routing">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SMART GATEWAY ROUTING & CASCADING OPTIMIZER PLANE"
          title="GATEWAY"
          highlightTitle="ROUTING & CASCADING"
          description="Autonomous payment gateway routing, AI least-cost cascading, PSP health monitoring, and instant fallback failover."
          icon={Network}
          statusBadge="● AI ROUTER OPTIMIZED"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ROUTING RULES" value={`${MOCK_GATEWAY_ROUTING.length}`} subtext="ACTIVE AI ROUTER RULES" accentColor="text-blue-400" />
          <AGMetricCard label="ROUTING SUCCESS" value="99.91%" subtext="PRIMARY / FALLBACK MATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="COST OPTIMIZATION" value="-18.4% SAVED" subtext="INTERCHANGE LEAST-COST" accentColor="text-emerald-400" />
          <AGMetricCard label="PSP FAILOVER SLA" value="< 50ms" subtext="INSTANT CASCADING SWITCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Rule ID, Rule Name, Gateway..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ROUTING_RULES', 'CASCADING', 'PSP_HEALTH', 'COST_OPTIMIZER', 'AUDIT'] as GatewayRoutingTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ROUTING_RULES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RULE ID</th>
                  <th className="p-3">RULE NAME</th>
                  <th className="p-3">PRIMARY GATEWAY</th>
                  <th className="p-3">FALLBACK GATEWAY</th>
                  <th className="p-3">CONDITION</th>
                  <th className="p-3">SUCCESS RATE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(g => (
                  <tr key={g.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{g.ruleId}</td>
                    <td className="p-3 font-bold text-slate-200">{g.ruleName}</td>
                    <td className="p-3 font-bold text-emerald-400">{g.primaryGateway}</td>
                    <td className="p-3 text-amber-400">{g.fallbackGateway}</td>
                    <td className="p-3 text-slate-300 font-mono">{g.condition}</td>
                    <td className="p-3 text-emerald-400 font-bold">{g.successRate}</td>
                    <td className="p-3"><AGBadge status={g.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ROUTING_RULES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
