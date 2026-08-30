'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Network, RefreshCw, Plus } from 'lucide-react';
import { GatewaysTabType } from '@/components/gateways/gateway-types';
import { MOCK_GATEWAYS } from '@/components/gateways/gateway-data';

export default function GatewaysPage() {
  const [activeTab, setActiveTab] = useState<GatewaysTabType>('CONNECTORS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_GATEWAYS.filter(g => 
      !search || g.gatewayId.toLowerCase().includes(search.toLowerCase()) || g.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="gateways">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PAYMENT GATEWAY & PSP CONNECTOR ORCHESTRATION"
          title="PAYMENT"
          highlightTitle="GATEWAYS"
          description="Multi-processor PSP routing, dynamic failover, connector latency telemetry, and payment gateway configuration."
          icon={Network}
          statusBadge="● 3 PSP CONNECTORS ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Add Connector Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ADD CONNECTOR</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="PSP CONNECTORS" value={`${MOCK_GATEWAYS.length}`} subtext="ACTIVE GATEWAY PIPELINES" accentColor="text-blue-400" />
          <AGMetricCard label="GLOBAL SUCCESS" value="99.94%" subtext="AUTH PASS RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG LATENCY" value="149ms" subtext="SUB-200MS PSP RESPONSE" accentColor="text-emerald-400" />
          <AGMetricCard label="FAILOVER ENGINE" value="AUTOMATIC" subtext="ZERO TRANSACTION LOSS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Gateway ID, Provider..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['CONNECTORS', 'ROUTING_RULES', 'HEALTH', 'LATENCY', 'FAILOVER', 'CONFIG', 'AUDIT'] as GatewaysTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'CONNECTORS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">GATEWAY ID</th>
                  <th className="p-3">CONNECTOR NAME</th>
                  <th className="p-3">PROVIDER</th>
                  <th className="p-3">REGION</th>
                  <th className="p-3">SUCCESS RATE</th>
                  <th className="p-3">AVG LATENCY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(g => (
                  <tr key={g.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{g.gatewayId}</td>
                    <td className="p-3 font-bold text-slate-200">{g.name}</td>
                    <td className="p-3 font-bold text-purple-400">{g.provider}</td>
                    <td className="p-3 text-slate-300">{g.region}</td>
                    <td className="p-3 font-bold text-emerald-400">{g.successRate}</td>
                    <td className="p-3 text-emerald-400 font-bold">{g.avgLatencyMs}ms</td>
                    <td className="p-3"><AGBadge status={g.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'CONNECTORS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
