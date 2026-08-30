'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Repeat, RefreshCw, Plus } from 'lucide-react';
import { SubscriptionsTabType } from '@/components/subscriptions/subscription-types';
import { MOCK_SUBSCRIPTIONS } from '@/components/subscriptions/subscription-data';

export default function SubscriptionsPage() {
  const [activeTab, setActiveTab] = useState<SubscriptionsTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SUBSCRIPTIONS.filter(s => 
      !search || s.subscriptionId.toLowerCase().includes(search.toLowerCase()) || s.planName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="subscriptions">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="RECURRING SUBSCRIPTION CONTROL PLANE"
          title="SUBSCRIPTION"
          highlightTitle="OPERATIONS"
          description="Autonomous agent subscription management, trial periods, automated renewals, dunning retries, and churn analytics."
          icon={Repeat}
          statusBadge="● SUBSCRIPTION ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('New Subscription Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> NEW SUBSCRIPTION</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SUBSCRIPTIONS" value={`${MOCK_SUBSCRIPTIONS.length}`} subtext="ACTIVE CONTRACTS" accentColor="text-blue-400" />
          <AGMetricCard label="MRR VOLUME" value="$7,498.00" subtext="MONTHLY RECURRING" accentColor="text-emerald-400" />
          <AGMetricCard label="ACTIVE RENEWALS" value="02" subtext="HEALTHY STATUS" accentColor="text-emerald-400" />
          <AGMetricCard label="CHURN RATE" value="0.00%" subtext="ZERO CANCELATIONS" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Subscription ID, Plan Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'PLANS', 'TRIALS', 'RENEWALS', 'CANCELLATIONS', 'DUNNING', 'EVENTS', 'AUDIT'] as SubscriptionsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SUB ID</th>
                  <th className="p-3">PLAN NAME</th>
                  <th className="p-3">CUSTOMER</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">PERIOD END</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.subscriptionId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.planName}</td>
                    <td className="p-3 text-slate-300">{s.customer}</td>
                    <td className="p-3 font-bold text-purple-400">{s.agentId}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.amount} / {s.interval}</td>
                    <td className="p-3 text-slate-400">{s.currentPeriodEnd}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'REGISTRY' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
