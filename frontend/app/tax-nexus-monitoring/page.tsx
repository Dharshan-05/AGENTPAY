'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Scale, RefreshCw } from 'lucide-react';
import { TaxNexusMonitoringTabType } from '@/components/tax-nexus-monitoring/tax-nexus-types';
import { MOCK_TAX_NEXUSES } from '@/components/tax-nexus-monitoring/tax-nexus-data';

export default function TaxNexusMonitoringPage() {
  const [activeTab, setActiveTab] = useState<TaxNexusMonitoringTabType>('NEXUS_JURISDICTIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TAX_NEXUSES.filter(n => 
      !search || n.nexusId.toLowerCase().includes(search.toLowerCase()) || n.jurisdiction.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="tax-nexus-monitoring">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="ECONOMIC TAX NEXUS & STATE THRESHOLD MONITORING PLANE"
          title="TAX NEXUS"
          highlightTitle="MONITORING"
          description="Real-time economic nexus threshold tracking, state sales tax liability monitoring, automated filing alerts, and multi-state compliance."
          icon={Scale}
          statusBadge="● TAX NEXUS MONITOR ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="MONITORED STATES" value={`${MOCK_TAX_NEXUSES.length}`} subtext="ACTIVE JURISDICTIONS" accentColor="text-blue-400" />
          <AGMetricCard label="NEXUS REACHED" value="1 STATE (CA)" subtext="FILING OBLIGATION ACTIVE" accentColor="text-amber-400" />
          <AGMetricCard label="APPROACHING THRESHOLD" value="1 STATE (NY)" subtext="83.7% OF THRESHOLD" accentColor="text-emerald-400" />
          <AGMetricCard label="CALCULATION ACCURACY" value="100% REAL-TIME" subtext="AUTOMATED NEXUS TRACKING" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Nexus ID, Jurisdiction..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['NEXUS_JURISDICTIONS', 'ECONOMIC_THRESHOLDS', 'TAX_LIABILITIES', 'AUDIT'] as TaxNexusMonitoringTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'NEXUS_JURISDICTIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">NEXUS ID</th>
                  <th className="p-3">JURISDICTION</th>
                  <th className="p-3">SALES VOLUME</th>
                  <th className="p-3">THRESHOLD LIMIT</th>
                  <th className="p-3">% REACHED</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(n => (
                  <tr key={n.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{n.nexusId}</td>
                    <td className="p-3 font-bold text-slate-200">{n.jurisdiction}</td>
                    <td className="p-3 font-bold text-emerald-400">{n.salesVolume}</td>
                    <td className="p-3 text-slate-300 font-mono">{n.thresholdLimit}</td>
                    <td className="p-3 text-amber-400 font-mono font-bold">{n.percentageReached}</td>
                    <td className="p-3"><AGBadge status={n.nexusStatus} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'NEXUS_JURISDICTIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
