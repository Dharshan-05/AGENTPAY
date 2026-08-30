'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Percent, RefreshCw } from 'lucide-react';
import { CommissionsTabType } from '@/components/commissions/commission-types';
import { MOCK_COMMISSIONS } from '@/components/commissions/commission-data';

export default function CommissionsPage() {
  const [activeTab, setActiveTab] = useState<CommissionsTabType>('COMMISSIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_COMMISSIONS.filter(c => 
      !search || c.commissionId.toLowerCase().includes(search.toLowerCase()) || c.agentId.toLowerCase().includes(search.toLowerCase()) || c.agentName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="commissions">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AGENT COMMISSION & REVENUE SHARING ENGINE"
          title="AGENT"
          highlightTitle="COMMISSIONS"
          description="Autonomous agent commission allocation, performance-based revenue splits, tier multipliers, and payout reconciliation."
          icon={Percent}
          statusBadge="● COMMISSION ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="AGENT COMMISSIONS" value={`${MOCK_COMMISSIONS.length}`} subtext="PROCESSED COMMISSIONS" accentColor="text-blue-400" />
          <AGMetricCard label="COMMISSION PAID" value="$2,135.00" subtext="TOTAL AGENT EARNINGS" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG COMMISSION RATE" value="2.25%" subtext="PER-TRANSACTION SPLIT" accentColor="text-emerald-400" />
          <AGMetricCard label="RECONCILIATION RATE" value="100%" subtext="ZERO VARIANCE MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Commission ID, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['COMMISSIONS', 'AGENTS', 'REVENUE_SPLITS', 'TIERS', 'PAYOUT_SCHEDULE', 'AUDIT'] as CommissionsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'COMMISSIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">COMMISSION ID</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">AGENT NAME</th>
                  <th className="p-3">COMMISSION</th>
                  <th className="p-3">RATE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.commissionId}</td>
                    <td className="p-3 font-bold text-purple-400">{c.agentId}</td>
                    <td className="p-3 font-bold text-slate-200">{c.agentName}</td>
                    <td className="p-3 font-bold text-emerald-400">{c.commissionAmount}</td>
                    <td className="p-3 text-slate-300">{c.rate}</td>
                    <td className="p-3"><AGBadge status={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'COMMISSIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
