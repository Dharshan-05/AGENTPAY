'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Activity, RefreshCw } from 'lucide-react';
import { HealthTabType } from '@/components/system-health/system-health-types';
import { MOCK_HEALTH } from '@/components/system-health/system-health-data';

export default function SystemHealthPage() {
  const [activeTab, setActiveTab] = useState<HealthTabType>('OVERVIEW');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_HEALTH.filter(h => 
      !search || h.componentId.toLowerCase().includes(search.toLowerCase()) || h.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="system-health">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SYSTEM HEALTH, CONNECTOR LATENCY & UPTIME CONTROL PLANE"
          title="SYSTEM"
          highlightTitle="HEALTH"
          description="Real-time PSP connector telemetry, circuit breaker trip states, sub-100ms latency monitoring, and zero-downtime health governance."
          icon={Activity}
          statusBadge="● ALL SYSTEMS OPERATIONAL"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SYSTEM COMPONENTS" value={`${MOCK_HEALTH.length}`} subtext="MONITORED SERVICES" accentColor="text-blue-400" />
          <AGMetricCard label="GLOBAL UPTIME" value="99.99%" subtext="30-DAY TELEMETRY" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG ENGINE LATENCY" value="28ms" subtext="SUB-50MS ENGINE SPEED" accentColor="text-emerald-400" />
          <AGMetricCard label="CIRCUIT BREAKERS" value="0 TRIP" subtext="ALL CONNECTORS HEALTHY" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Component ID, Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['OVERVIEW', 'LATENCY_MAP', 'CIRCUIT_BREAKERS', 'Uptime', 'CONNECTORS', 'INCIDENTS', 'AUDIT'] as HealthTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'OVERVIEW' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">COMPONENT ID</th>
                  <th className="p-3">SERVICE NAME</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">UPTIME (30D)</th>
                  <th className="p-3">LATENCY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(h => (
                  <tr key={h.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{h.componentId}</td>
                    <td className="p-3 font-bold text-slate-200">{h.name}</td>
                    <td className="p-3 font-bold text-purple-400">{h.type}</td>
                    <td className="p-3 text-emerald-400 font-bold">{h.uptime99}</td>
                    <td className="p-3 text-emerald-400 font-bold">{h.latencyMs}ms</td>
                    <td className="p-3"><AGBadge status={h.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'OVERVIEW' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
