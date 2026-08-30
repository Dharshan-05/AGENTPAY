'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { ShieldCheck, RefreshCw } from 'lucide-react';
import { ChargebackAutoDefenseTabType } from '@/components/chargeback-auto-defense/chargeback-auto-defense-types';
import { MOCK_CHARGEBACK_AUTO_DEFENSES } from '@/components/chargeback-auto-defense/chargeback-auto-defense-data';

export default function ChargebackAutoDefensePage() {
  const [activeTab, setActiveTab] = useState<ChargebackAutoDefenseTabType>('AUTO_EVIDENCE_JOBS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_CHARGEBACK_AUTO_DEFENSES.filter(a => 
      !search || a.defenseId.toLowerCase().includes(search.toLowerCase()) || a.disputeRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="chargeback-auto-defense">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AUTOMATED CHARGEBACK EVIDENCE GENERATION & DEFENSE PLANE"
          title="CHARGEBACK"
          highlightTitle="AUTO-DEFENSE"
          description="Automated dispute evidence packet compilation, cryptographic agent log proof generation, and win-rate maximization."
          icon={ShieldCheck}
          statusBadge="● AUTO-DEFENSE ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="AUTO-DEFENDED DISPUTES" value={`${MOCK_CHARGEBACK_AUTO_DEFENSES.length}`} subtext="EVIDENCE SUBMITTED" accentColor="text-blue-400" />
          <AGMetricCard label="DEFENSE WIN RATE" value="97.4%" subtext="HIGH WIN RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="PROOF GENERATION" value="< 500ms" subtext="AUTOMATED COMPILATION" accentColor="text-emerald-400" />
          <AGMetricCard label="RECOVERED VOLUME" value="$14,250.00" subtext="RECOVERED DISPUTE FUNDS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Defense ID, Dispute Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['AUTO_EVIDENCE_JOBS', 'WIN_RATE_RULES', 'TEMPLATES', 'AUDIT'] as ChargebackAutoDefenseTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'AUTO_EVIDENCE_JOBS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">DEFENSE ID</th>
                  <th className="p-3">DISPUTE REF</th>
                  <th className="p-3">EVIDENCE TYPE</th>
                  <th className="p-3">COMPILED PROOF HASH</th>
                  <th className="p-3">WIN PROBABILITY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(a => (
                  <tr key={a.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{a.defenseId}</td>
                    <td className="p-3 font-bold text-purple-400">{a.disputeRef}</td>
                    <td className="p-3 text-slate-200 font-mono">{a.evidenceType}</td>
                    <td className="p-3 text-slate-400 font-mono">{a.compiledProofHash}</td>
                    <td className="p-3 text-emerald-400 font-bold">{a.winProbability}</td>
                    <td className="p-3"><AGBadge status={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'AUTO_EVIDENCE_JOBS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
