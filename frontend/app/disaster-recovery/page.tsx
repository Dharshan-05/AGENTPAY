'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Server, RefreshCw } from 'lucide-react';
import { DisasterRecoveryTabType } from '@/components/disaster-recovery/disaster-recovery-types';
import { MOCK_DISASTER_RECOVERIES } from '@/components/disaster-recovery/disaster-recovery-data';

export default function DisasterRecoveryPage() {
  const [activeTab, setActiveTab] = useState<DisasterRecoveryTabType>('FAILOVER_NODES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_DISASTER_RECOVERIES.filter(d => 
      !search || d.disasterRecoveryId.toLowerCase().includes(search.toLowerCase()) || d.region.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="disaster-recovery">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-REGION HIGH-AVAILABILITY & DISASTER RECOVERY FAILOVER PLANE"
          title="DISASTER RECOVERY"
          highlightTitle="& HA FAILOVER"
          description="Multi-region active-active cluster failover, RPO/RTO real-time SLA verification, automated DB snapshot replication, and zero-downtime HA routing."
          icon={Server}
          statusBadge="● MULTI-REGION HA ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="FAILOVER NODES" value={`${MOCK_DISASTER_RECOVERIES.length}`} subtext="HOT STANDBY CLUSTERS" accentColor="text-blue-400" />
          <AGMetricCard label="RPO TELEMETRY" value="0 SECONDS" subtext="ZERO DATA LOSS" accentColor="text-emerald-400" />
          <AGMetricCard label="RTO TELEMETRY" value="< 2 SECONDS" subtext="SUB-SECOND FAILOVER" accentColor="text-emerald-400" />
          <AGMetricCard label="HA REPLICATION" value="ACTIVE-ACTIVE" subtext="MULTI-REGION SYNC" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search DR ID, Region..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['FAILOVER_NODES', 'RPO_RTO_TELEMETRY', 'BACKUP_SNAPSHOTS', 'HA_HEALTH', 'AUDIT'] as DisasterRecoveryTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'FAILOVER_NODES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">DR ID</th>
                  <th className="p-3">REGION</th>
                  <th className="p-3">FAILOVER MODE</th>
                  <th className="p-3">RPO SLA</th>
                  <th className="p-3">RTO SLA</th>
                  <th className="p-3">LAST DR TEST</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{d.disasterRecoveryId}</td>
                    <td className="p-3 text-slate-300">{d.region}</td>
                    <td className="p-3 font-bold text-purple-400">{d.failoverMode}</td>
                    <td className="p-3 font-mono text-emerald-400 font-bold">{d.rpoSeconds}s</td>
                    <td className="p-3 font-mono text-emerald-400 font-bold">{d.rtoSeconds}s</td>
                    <td className="p-3 text-slate-400">{d.lastDrTest}</td>
                    <td className="p-3"><AGBadge status={d.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'FAILOVER_NODES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
