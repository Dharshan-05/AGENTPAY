'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { Cpu, RefreshCw, Download, Plus, ArrowRight } from 'lucide-react';
import { RiskRulesTabType, RiskRuleRecord } from '@/components/risk-rules/risk-rule-types';
import { MOCK_RISK_RULES } from '@/components/risk-rules/risk-rule-data';

export default function RiskRulesPage() {
  const [activeTab, setActiveTab] = useState<RiskRulesTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedRule, setSelectedRule] = useState<RiskRuleRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_RISK_RULES.filter(r => 
      !search || r.ruleId.toLowerCase().includes(search.toLowerCase()) || r.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="risk-rules">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="FRAUDGUARD DECISION & RULE ENGINE"
          title="RISK RULES &"
          highlightTitle="DECISIONS"
          description="Autonomous risk evaluation rules, velocity threshold conditions, decision policy actions (ALLOW / REVIEW / BLOCK / HITL), and model accuracy metrics."
          icon={Cpu}
          statusBadge="● FRAUD ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Create Rule Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> CREATE RULE</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="RISK RULES" value={`${MOCK_RISK_RULES.length}`} subtext="ACTIVE DECISION RULES" accentColor="text-purple-400" />
          <AGMetricCard label="EVALUATIONS 24H" value="18,420" subtext="IN-LINE DECISIONS" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTO-BLOCKED" value="142" subtext="HIGH-RISK STOPS" accentColor="text-rose-400" />
          <AGMetricCard label="HITL ESCALATED" value="28" subtext="HUMAN APPROVALS" accentColor="text-amber-400" />
          <AGMetricCard label="FALSE POSITIVE" value="0.02%" subtext="PRECISION RATE 99.98%" accentColor="text-blue-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Rule ID, Rule Name, Condition..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'RULES', 'CONDITIONS', 'ACTIONS', 'TESTING', 'DECISIONS', 'PERFORMANCE', 'AUDIT'] as RiskRulesTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">RULE ID</th>
                  <th className="p-3">PRIORITY &amp; NAME</th>
                  <th className="p-3">CONDITION</th>
                  <th className="p-3">ACTION</th>
                  <th className="p-3">THRESHOLD</th>
                  <th className="p-3">TRIGGERED</th>
                  <th className="p-3">FALSE POSITIVE</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} onClick={() => setSelectedRule(r)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-purple-400">{r.ruleId}</td>
                    <td className="p-3"><div className="font-bold text-slate-200">P{r.priority} — {r.name}</div><div className="text-[10px] text-slate-500">{r.agentScope}</div></td>
                    <td className="p-3 text-slate-400 font-mono text-[10px]">{r.condition}</td>
                    <td className="p-3 font-bold"><span className={r.action === 'BLOCK' ? 'text-rose-400' : r.action === 'HITL' ? 'text-amber-400' : 'text-emerald-400'}>{r.action}</span></td>
                    <td className="p-3 font-bold text-blue-400">{r.riskThreshold}/100</td>
                    <td className="p-3 text-slate-200 font-bold">{r.triggeredCount}</td>
                    <td className="p-3 text-emerald-400">{r.falsePositiveRate}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 3 FRAUDGUARD RULES EVALUATING
          </div>
        )}

        {selectedRule && (
          <AGDrawer isOpen={!!selectedRule} onClose={() => setSelectedRule(null)} title={`RULE INSPECTOR: ${selectedRule.ruleId}`} subtitle="FRAUDGUARD RULE LOGIC">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/20 space-y-1">
                <div className="text-[9px] text-purple-400 font-bold uppercase">RULE ACTION</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedRule.ruleId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-amber-400 font-bold">{selectedRule.condition}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-rose-400 font-bold">{selectedRule.action}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Rule Name:</span><span className="text-slate-200 font-bold">{selectedRule.name}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Triggered:</span><span className="text-emerald-400 font-bold">{selectedRule.triggeredCount} times</span></div>
                <div className="flex justify-between"><span className="text-slate-500">False Positive Rate:</span><span className="text-emerald-400 font-bold">{selectedRule.falsePositiveRate}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
