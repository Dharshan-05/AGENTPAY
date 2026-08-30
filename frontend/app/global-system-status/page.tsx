'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Server, RefreshCw } from 'lucide-react';
import { GlobalSystemStatusTabType } from '@/components/global-system-status/global-system-status-types';
import { MOCK_GLOBAL_SYSTEM_STATUSES } from '@/components/global-system-status/global-system-status-data';

export default function GlobalSystemStatusPage() {
  const [activeTab, setActiveTab] = useState<GlobalSystemStatusTabType>('SYSTEM_STATUS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_GLOBAL_SYSTEM_STATUSES.filter(s => 
      !search || s.statusId.toLowerCase().includes(search.toLowerCase()) || s.subsystemName.toLowerCase().includes(search.toLowerCase()) || s.operatingRegion.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="global-system-status">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ENTERPRISE GLOBAL SYSTEM STATUS & MULTI-REGION SLA MONITORING PLANE"
          title="GLOBAL SYSTEM"
          highlightTitle="STATUS & SLA"
          description="Multi-region infrastructure availability monitoring, sub-20ms global API latency mapping, 99.999% SLA tracking, and live health telemetry."
          icon={Server}
          statusBadge="● ALL SYSTEMS OPERATIONAL (99.999%)"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="GLOBAL UPTIME (90D)" value="99.999%" subtext="FIVE-NINES SLA PASS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG GLOBAL LATENCY" value="16ms" subtext="SUB-20MS RESPONSIVENESS" accentColor="text-emerald-400" />
          <AGMetricCard label="MONITORED SUBSYSTEMS" value={`${MOCK_GLOBAL_SYSTEM_STATUSES.length}`} subtext="100% OPERATIONAL" accentColor="text-blue-400" />
          <AGMetricCard label="ACTIVE INCIDENTS" value="0 INCIDENTS" subtext="ZERO SYSTEM IMPACT" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Status ID, Subsystem, Region..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SYSTEM_STATUS', 'REGION_LATENCY_MAP', 'INCIDENT_HISTORY', 'SLA_METRICS', 'AUDIT'] as GlobalSystemStatusTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SYSTEM_STATUS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">STATUS ID</th>
                  <th className="p-3">SUBSYSTEM NAME</th>
                  <th className="p-3">OPERATING REGION</th>
                  <th className="p-3">90D UPTIME</th>
                  <th className="p-3">CURRENT LATENCY</th>
                  <th className="p-3">HEALTH STATE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.statusId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.subsystemName}</td>
                    <td className="p-3 text-purple-400 font-mono">{s.operatingRegion}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.uptime90d}</td>
                    <td className="p-3 text-emerald-400 font-mono font-bold">{s.currentLatencyMs} ms</td>
                    <td className="p-3"><AGBadge status={s.healthState} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SYSTEM_STATUS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
