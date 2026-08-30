'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Percent, RefreshCw } from 'lucide-react';
import { PayoutSplitRulesTabType } from '@/components/payout-split-rules/payout-split-rule-types';
import { MOCK_PAYOUT_SPLIT_RULES } from '@/components/payout-split-rules/payout-split-rule-data';

export default function PayoutSplitRulesPage() {
  const [activeTab, setActiveTab] = useState<PayoutSplitRulesTabType>('SPLIT_RULES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_PAYOUT_SPLIT_RULES.filter(s => 
      !search || s.ruleId.toLowerCase().includes(search.toLowerCase()) || s.ruleName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="payout-split-rules">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-PARTY PAYOUT SPLIT RULES & COMMISSION MATRIX PLANE"
          title="PAYOUT SPLIT"
          highlightTitle="RULES"
          description="Multi-party transaction split rules, vendor payout allocations, platform take-rate calculations, and autonomous agent commission splits."
          icon={Percent}
          statusBadge="● SPLIT MATRIX ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SPLIT RULES" value={`${MOCK_PAYOUT_SPLIT_RULES.length}`} subtext="ACTIVE REVENUE MATRICES" accentColor="text-blue-400" />
          <AGMetricCard label="AVG PLATFORM TAKE RATE" value="12.5%" subtext="NET PLATFORM MARGIN" accentColor="text-emerald-400" />
          <AGMetricCard label="VENDOR ALLOCATION" value="84.0%" subtext="DIRECT VENDOR PAYOUT" accentColor="text-emerald-400" />
          <AGMetricCard label="AGENT COMMISSIONS" value="3.5%" subtext="AUTONOMOUS AGENT REWARD" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Rule ID, Rule Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SPLIT_RULES', 'MARKETPLACE_REVENUE', 'AGENT_COMMISSIONS', 'AUDIT'] as PayoutSplitRulesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SPLIT_RULES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RULE ID</th>
                  <th className="p-3">RULE NAME</th>
                  <th className="p-3">PLATFORM SHARE</th>
                  <th className="p-3">VENDOR SHARE</th>
                  <th className="p-3">AGENT COMMISSION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.ruleId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.ruleName}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.platformShare}</td>
                    <td className="p-3 text-slate-300 font-bold">{s.vendorShare}</td>
                    <td className="p-3 text-purple-400 font-mono font-bold">{s.agentCommission}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SPLIT_RULES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
