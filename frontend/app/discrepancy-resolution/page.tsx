'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { DiscrepancyResolutionTabType } from '@/components/discrepancy-resolution/discrepancy-resolution-types';
import { MOCK_DISCREPANCY_RESOLUTIONS } from '@/components/discrepancy-resolution/discrepancy-resolution-data';

export default function DiscrepancyResolutionPage() {
  const [activeTab, setActiveTab] = useState<DiscrepancyResolutionTabType>('EXCEPTIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_DISCREPANCY_RESOLUTIONS.filter(d => 
      !search || d.discrepancyId.toLowerCase().includes(search.toLowerCase()) || d.ledgerEntryRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="discrepancy-resolution">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="LEDGER DISCREPANCY & AUTOMATED EXCEPTION RESOLUTION PLANE"
          title="DISCREPANCY"
          highlightTitle="RESOLUTION"
          description="Automated ledger exception matching, micro-timing variance adjustment, double-entry audit balancing, and zero-loss write-offs."
          icon={AlertTriangle}
          statusBadge="● EXCEPTION RESOLUTION ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="OPEN DISCREPANCIES" value="0 OPEN" subtext="ALL EXCEPTIONS RESOLVED" accentColor="text-emerald-400" />
          <AGMetricCard label="AUTO-RESOLVE RATE" value="100.0%" subtext="ZERO MANUAL INTERVENTION" accentColor="text-emerald-400" />
          <AGMetricCard label="NET VARIANCE" value="$0.00 ZERO" subtext="PERFECT LEDGER MATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="AUDIT INTEGRITY" value="BALANCED" subtext="DOUBLE-ENTRY VERIFIED" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Discrepancy ID, Ledger Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['EXCEPTIONS', 'AUTOMATED_ADJUSTMENTS', 'WRITE_OFFS', 'AUDIT'] as DiscrepancyResolutionTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'EXCEPTIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">DISCREPANCY ID</th>
                  <th className="p-3">LEDGER REF</th>
                  <th className="p-3">PROCESSOR REF</th>
                  <th className="p-3">VARIANCE</th>
                  <th className="p-3">REASON</th>
                  <th className="p-3">STRATEGY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{d.discrepancyId}</td>
                    <td className="p-3 font-bold text-purple-400">{d.ledgerEntryRef}</td>
                    <td className="p-3 text-slate-300 font-mono">{d.processorRef}</td>
                    <td className="p-3 font-bold text-emerald-400">{d.varianceAmount}</td>
                    <td className="p-3 text-slate-300 font-mono">{d.discrepancyReason}</td>
                    <td className="p-3 text-slate-400 font-mono">{d.resolutionStrategy}</td>
                    <td className="p-3"><AGBadge status={d.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'EXCEPTIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
