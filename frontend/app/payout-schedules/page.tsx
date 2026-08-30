'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ArrowUpRight, RefreshCw } from 'lucide-react';
import { PayoutSchedulesTabType } from '@/components/payout-schedules/payout-schedule-types';
import { MOCK_PAYOUT_SCHEDULES } from '@/components/payout-schedules/payout-schedule-data';

export default function PayoutSchedulesPage() {
  const [activeTab, setActiveTab] = useState<PayoutSchedulesTabType>('SCHEDULES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PAYOUT_SCHEDULES.filter(p => 
      !search || p.scheduleId.toLowerCase().includes(search.toLowerCase()) || p.accountRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payout-schedules">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="PAYOUT SCHEDULING & ROLLING RESERVE CONTROL PLANE"
          title="PAYOUT"
          highlightTitle="SCHEDULES"
          description="Merchant payout scheduling, rolling reserve percentage holds, automated payout cadence triggers, and direct bank routing."
          icon={ArrowUpRight}
          statusBadge="● PAYOUT CADENCE ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="PAYOUT SCHEDULES" value={`${MOCK_PAYOUT_SCHEDULES.length}`} subtext="ACTIVE PAYOUT CADENCES" accentColor="text-blue-400" />
          <AGMetricCard label="NEXT PAYOUT BATCH" value="$184,200.00" subtext="DUE 2026-08-31" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG ROLLING RESERVE" value="7.5%" subtext="HOLD RESERVES" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTOMATED DISPATCH" value="100% AUTOMATED" subtext="ZERO MANUAL INTERVENTION" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Schedule ID, Account Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SCHEDULES', 'RESERVE_HOLDS', 'PAYOUT_METHODS', 'AUTOMATED_TRIGGERS', 'AUDIT'] as PayoutSchedulesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SCHEDULES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SCHEDULE ID</th>
                  <th className="p-3">ACCOUNT REF</th>
                  <th className="p-3">CADENCE</th>
                  <th className="p-3">ROLLING RESERVE</th>
                  <th className="p-3">NEXT PAYOUT</th>
                  <th className="p-3">PAYOUT METHOD</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{p.scheduleId}</td>
                    <td className="p-3 font-bold text-slate-200">{p.accountRef}</td>
                    <td className="p-3 font-bold text-purple-400">{p.cadence}</td>
                    <td className="p-3 text-amber-400">{p.rollingReservePercent}</td>
                    <td className="p-3 text-emerald-400 font-bold">{p.nextPayoutDate}</td>
                    <td className="p-3 text-slate-300 font-mono">{p.payoutMethod}</td>
                    <td className="p-3"><AGBadge status={p.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SCHEDULES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
