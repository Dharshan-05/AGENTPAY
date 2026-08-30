'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Zap, RefreshCw } from 'lucide-react';
import { AgentSpendVelocityTabType } from '@/components/agent-spend-velocity/agent-spend-velocity-types';
import { MOCK_AGENT_SPEND_VELOCITIES } from '@/components/agent-spend-velocity/agent-spend-velocity-data';

export default function AgentSpendVelocityPage() {
  const [activeTab, setActiveTab] = useState<AgentSpendVelocityTabType>('VELOCITY_LIMITS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_AGENT_SPEND_VELOCITIES.filter(v => 
      !search || v.velocityId.toLowerCase().includes(search.toLowerCase()) || v.agentRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="agent-spend-velocity">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AUTONOMOUS AGENT SPENDING VELOCITY & BURST CONTROL PLANE"
          title="AGENT SPEND"
          highlightTitle="VELOCITY"
          description="Autonomous AI agent spend velocity limits, sliding window hourly caps, rapid burst anomaly prevention, and policy safety throttles."
          icon={Zap}
          statusBadge="● VELOCITY CONTROLS LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="MONITORED AGENTS" value={`${MOCK_AGENT_SPEND_VELOCITIES.length}`} subtext="ACTIVE VELOCITY RULES" accentColor="text-blue-400" />
          <AGMetricCard label="HOURLY SPEND CAP" value="$15,000.00" subtext="SLIDING WINDOW TOTAL" accentColor="text-emerald-400" />
          <AGMetricCard label="CURRENT HOURLY SPEND" value="$4,340.00" subtext="28.9% OF TOTAL CAP" accentColor="text-emerald-400" />
          <AGMetricCard label="BURST ANOMALIES" value="0 BLOCKED" subtext="ZERO VELOCITY VIOLATIONS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Velocity ID, Agent Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['VELOCITY_LIMITS', 'BURST_DETECTION', 'HOURLY_WINDOW_MONITOR', 'AUDIT'] as AgentSpendVelocityTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'VELOCITY_LIMITS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">VELOCITY ID</th>
                  <th className="p-3">AGENT REF</th>
                  <th className="p-3">HOURLY LIMIT</th>
                  <th className="p-3">HOURLY SPENT</th>
                  <th className="p-3">BURST THRESHOLD</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(v => (
                  <tr key={v.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{v.velocityId}</td>
                    <td className="p-3 font-bold text-slate-200">{v.agentRef}</td>
                    <td className="p-3 font-bold text-purple-400">{v.hourlyLimit}</td>
                    <td className="p-3 text-emerald-400 font-mono font-bold">{v.hourlySpent}</td>
                    <td className="p-3 text-amber-400 font-mono">{v.burstThreshold}</td>
                    <td className="p-3"><AGBadge status={v.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'VELOCITY_LIMITS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
