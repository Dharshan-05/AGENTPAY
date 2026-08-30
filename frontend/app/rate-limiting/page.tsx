'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Activity, RefreshCw } from 'lucide-react';
import { RateLimitingTabType } from '@/components/rate-limiting/rate-limiting-types';
import { MOCK_RATE_LIMITINGS } from '@/components/rate-limiting/rate-limiting-data';

export default function RateLimitingPage() {
  const [activeTab, setActiveTab] = useState<RateLimitingTabType>('LIMIT_POLICIES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_RATE_LIMITINGS.filter(r => 
      !search || r.limitId.toLowerCase().includes(search.toLowerCase()) || r.clientRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="rate-limiting">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="API RATE LIMITING & LEAKY-BUCKET THROTTLING PLANE"
          title="RATE LIMITING"
          highlightTitle="& THROTTLING"
          description="Autonomous agent RPS quota enforcement, leaky-bucket burst control, IP CIDR throttling buckets, and DDoS mitigation SLA."
          icon={Activity}
          statusBadge="● RATE LIMIT ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE LIMIT POLICIES" value={`${MOCK_RATE_LIMITINGS.length}`} subtext="ENFORCED QUOTAS" accentColor="text-blue-400" />
          <AGMetricCard label="PEAK RPS CAPACITY" value="700 RPS" subtext="MAX ALLOWED BURST" accentColor="text-emerald-400" />
          <AGMetricCard label="THROTTLED REQUESTS" value="0 REJECTS" subtext="100% HEALTHY TRAFFIC" accentColor="text-emerald-400" />
          <AGMetricCard label="ALGORITHM" value="LEAKY BUCKET" subtext="SUB-MILLISECOND SLA" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Limit ID, Client Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['LIMIT_POLICIES', 'BURST_CONTROLS', 'THROTTLED_CLIENTS', 'IP_BUCKETS', 'AUDIT'] as RateLimitingTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'LIMIT_POLICIES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">LIMIT ID</th>
                  <th className="p-3">CLIENT REF</th>
                  <th className="p-3">MAX RPS</th>
                  <th className="p-3">BURST CAPACITY</th>
                  <th className="p-3">CURRENT RPS</th>
                  <th className="p-3">THROTTLED 24H</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.limitId}</td>
                    <td className="p-3 font-bold text-slate-200">{r.clientRef}</td>
                    <td className="p-3 font-bold text-purple-400">{r.maxRps} RPS</td>
                    <td className="p-3 text-emerald-400 font-mono font-bold">{r.burstCapacity} RPS</td>
                    <td className="p-3 text-emerald-400 font-mono">{r.currentRps} RPS</td>
                    <td className="p-3 text-slate-400 font-mono">{r.throttledRequests24h}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'LIMIT_POLICIES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
