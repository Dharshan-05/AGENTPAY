'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Award, RefreshCw } from 'lucide-react';
import { LoyaltyTabType } from '@/components/loyalty/loyalty-types';
import { MOCK_LOYALTY } from '@/components/loyalty/loyalty-data';

export default function LoyaltyPage() {
  const [activeTab, setActiveTab] = useState<LoyaltyTabType>('MEMBERS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_LOYALTY.filter(l => 
      !search || l.memberId.toLowerCase().includes(search.toLowerCase()) || l.customerName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="loyalty">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="LOYALTY PROGRAM & REWARDS POINTS CONTROL PLANE"
          title="LOYALTY &"
          highlightTitle="REWARDS"
          description="Autonomous agent reward points accrual, VIP tier management, instant points-to-cash redemption, and loyalty analytics."
          icon={Award}
          statusBadge="● LOYALTY ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="LOYALTY MEMBERS" value={`${MOCK_LOYALTY.length}`} subtext="ACTIVE REWARD ACCOUNTS" accentColor="text-blue-400" />
          <AGMetricCard label="POINTS OUTSTANDING" value="213.6K Pts" subtext="TOTAL ACCRUED BALANCES" accentColor="text-emerald-400" />
          <AGMetricCard label="REDEEMED POINTS 24H" value="12,500 Pts" subtext="POINTS CONVERTED" accentColor="text-emerald-400" />
          <AGMetricCard label="TOP TIER RATIO" value="100% VIP" subtext="TITANIUM / PLATINUM" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Member ID, Customer..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['MEMBERS', 'ACCRUALS', 'REDEMPTIONS', 'TIERS', 'RULES', 'REWARDS', 'AUDIT'] as LoyaltyTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'MEMBERS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">MEMBER ID</th>
                  <th className="p-3">CUSTOMER NAME</th>
                  <th className="p-3">REWARD TIER</th>
                  <th className="p-3">POINTS BALANCE</th>
                  <th className="p-3">LIFETIME POINTS</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(l => (
                  <tr key={l.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{l.memberId}</td>
                    <td className="p-3 font-bold text-slate-200">{l.customerName}</td>
                    <td className="p-3 font-bold text-purple-400">{l.tier}</td>
                    <td className="p-3 font-bold text-emerald-400">{l.pointsBalance.toLocaleString()} pts</td>
                    <td className="p-3 text-slate-400">{l.lifetimePoints.toLocaleString()} pts</td>
                    <td className="p-3"><AGBadge status={l.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'MEMBERS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
