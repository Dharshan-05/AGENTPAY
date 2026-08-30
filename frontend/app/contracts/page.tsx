'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { FileCode, RefreshCw, Plus } from 'lucide-react';
import { ContractsTabType } from '@/components/contracts/contract-types';
import { MOCK_CONTRACTS } from '@/components/contracts/contract-data';

export default function ContractsPage() {
  const [activeTab, setActiveTab] = useState<ContractsTabType>('REGISTRY');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_CONTRACTS.filter(c => 
      !search || c.contractId.toLowerCase().includes(search.toLowerCase()) || c.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="contracts">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SMART CONTRACT & AUTONOMOUS EXECUTION CONTROL PLANE"
          title="SMART"
          highlightTitle="CONTRACTS"
          description="Autonomous agent smart contract state machine, programmatic spend caps, execution logs, and immutable policy enforcement."
          icon={FileCode}
          statusBadge="● CONTRACT ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Deploy Contract Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> DEPLOY CONTRACT</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="ACTIVE CONTRACTS" value={`${MOCK_CONTRACTS.length}`} subtext="ENFORCED STATE MACHINES" accentColor="text-blue-400" />
          <AGMetricCard label="SPEND CAP ENFORCED" value="$100.0K" subtext="MAX AUTONOMOUS LIMIT" accentColor="text-emerald-400" />
          <AGMetricCard label="EXECUTION LATENCY" value="14ms" subtext="SUB-20MS STATE COMPUTE" accentColor="text-emerald-400" />
          <AGMetricCard label="POLICY BOUND" value="100%" subtext="AGENTGUARD VERIFIED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Contract ID, Name, Agent..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'ACTIVE', 'EXECUTION_LOGS', 'STATE_MACHINES', 'POLICY_BOUND', 'TERMINATED', 'AUDIT'] as ContractsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">CONTRACT ID</th>
                  <th className="p-3">CONTRACT NAME</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">MERCHANT ID</th>
                  <th className="p-3">SPEND CAP</th>
                  <th className="p-3">POLICY REF</th>
                  <th className="p-3">STATE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.contractId}</td>
                    <td className="p-3 font-bold text-slate-200">{c.name}</td>
                    <td className="p-3 font-bold text-purple-400">{c.agentId}</td>
                    <td className="p-3 text-slate-300">{c.merchantId}</td>
                    <td className="p-3 font-bold text-emerald-400">{c.spendCap}</td>
                    <td className="p-3 text-slate-400">{c.policyRef}</td>
                    <td className="p-3"><AGBadge status={c.executionState} size="sm" /></td>
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
