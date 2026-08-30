'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { RefreshCw } from 'lucide-react';
import { RecurringTabType } from '@/components/recurring-payments/recurring-payment-types';
import { MOCK_RECURRING } from '@/components/recurring-payments/recurring-payment-data';

export default function RecurringPaymentsPage() {
  const [activeTab, setActiveTab] = useState<RecurringTabType>('SCHEDULE');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_RECURRING.filter(r => 
      !search || r.recurringId.toLowerCase().includes(search.toLowerCase()) || r.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="recurring-payments">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="DUNNING & RECURRING EXECUTION CONTROL PLANE"
          title="RECURRING"
          highlightTitle="PAYMENTS"
          description="Automated recurring payment execution schedules, smart dunning retry cadence, mandate linking, and intelligent routing."
          icon={RefreshCw}
          statusBadge="● RECURRING SCHEDULER ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SCHEDULED PAYMENTS" value={`${MOCK_RECURRING.length}`} subtext="IN-FLIGHT SCHEDULES" accentColor="text-blue-400" />
          <AGMetricCard label="DUNNING SUCCESS" value="99.8%" subtext="SMART RETRY RECOVERY" accentColor="text-emerald-400" />
          <AGMetricCard label="NEXT BATCH" value="01 Sep 2026" subtext="AUTOMATED DISPATCH" accentColor="text-purple-400" />
          <AGMetricCard label="RETRY LATENCY" value="12ms" subtext="OPTIMAL EXECUTION" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Recurring ID, Agent ID..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SCHEDULE', 'EXECUTIONS', 'DUNNING_RETRY', 'SUCCESSFUL', 'FAILED', 'SMART_ROUTING', 'AUDIT'] as RecurringTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SCHEDULE' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RECURRING ID</th>
                  <th className="p-3">MANDATE REF</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">NEXT EXECUTION</th>
                  <th className="p-3">RETRY ATTEMPT</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{r.recurringId}</td>
                    <td className="p-3 font-bold text-purple-400">{r.mandateRef}</td>
                    <td className="p-3 text-slate-200">{r.agentId}</td>
                    <td className="p-3 font-bold text-emerald-400">{r.amount}</td>
                    <td className="p-3 text-slate-400">{r.nextExecutionDate}</td>
                    <td className="p-3 text-slate-400">{r.retryAttempt}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SCHEDULE' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
