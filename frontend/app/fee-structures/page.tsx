'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Percent, RefreshCw } from 'lucide-react';
import { FeeStructuresTabType } from '@/components/fee-structures/fee-structure-types';
import { MOCK_FEE_STRUCTURES } from '@/components/fee-structures/fee-structure-data';

export default function FeeStructuresPage() {
  const [activeTab, setActiveTab] = useState<FeeStructuresTabType>('STRUCTURES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_FEE_STRUCTURES.filter(f => 
      !search || f.feeStructureId.toLowerCase().includes(search.toLowerCase()) || f.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="fee-structures">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="INTERCHANGE++ & FEE STRUCTURE MATRIX PLANE"
          title="FEE"
          highlightTitle="STRUCTURES & INTERCHANGE"
          description="Interchange++ fee models, card brand scheme fee matrices, volume tier discount schedules, and agent fee splitting rules."
          icon={Percent}
          statusBadge="● FEE MATRIX ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="FEE STRUCTURES" value={`${MOCK_FEE_STRUCTURES.length}`} subtext="ACTIVE INTERCHANGE RULES" accentColor="text-blue-400" />
          <AGMetricCard label="AVG EFFECTIVE RATE" value="1.95%" subtext="NET BLENDED COST" accentColor="text-emerald-400" />
          <AGMetricCard label="INTERCHANGE SAVINGS" value="$12,450.00" subtext="OPT-IN SAVINGS 30D" accentColor="text-emerald-400" />
          <AGMetricCard label="SCHEME FEE MATRIX" value="VISA / MC / AMEX" subtext="AUTOMATED COMPLIANCE" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Fee ID, Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['STRUCTURES', 'INTERCHANGE_PLUS', 'TIERED_RATES', 'AGENT_SPLITS', 'AUDIT'] as FeeStructuresTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'STRUCTURES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">FEE STRUCTURE ID</th>
                  <th className="p-3">NAME</th>
                  <th className="p-3">MODEL</th>
                  <th className="p-3">PERCENTAGE FEE</th>
                  <th className="p-3">FIXED FEE</th>
                  <th className="p-3">INTERCHANGE CAP</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(f => (
                  <tr key={f.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{f.feeStructureId}</td>
                    <td className="p-3 font-bold text-slate-200">{f.name}</td>
                    <td className="p-3 font-bold text-purple-400">{f.model}</td>
                    <td className="p-3 font-bold text-emerald-400">{f.percentageFee}</td>
                    <td className="p-3 text-slate-300">{f.fixedFee}</td>
                    <td className="p-3 text-amber-400 font-mono">{f.interchangeCap}</td>
                    <td className="p-3"><AGBadge status={f.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'STRUCTURES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
