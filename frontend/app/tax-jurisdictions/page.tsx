'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Building, RefreshCw } from 'lucide-react';
import { TaxJurisdictionsTabType } from '@/components/tax-jurisdictions/tax-jurisdiction-types';
import { MOCK_TAX_JURISDICTIONS } from '@/components/tax-jurisdictions/tax-jurisdiction-data';

export default function TaxJurisdictionsPage() {
  const [activeTab, setActiveTab] = useState<TaxJurisdictionsTabType>('JURISDICTIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TAX_JURISDICTIONS.filter(t => 
      !search || t.jurisdictionId.toLowerCase().includes(search.toLowerCase()) || t.regionName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="tax-jurisdictions">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="GLOBAL TAX JURISDICTION & NEXUS COMPLIANCE MATRIX"
          title="TAX"
          highlightTitle="JURISDICTIONS"
          description="Global tax jurisdiction matrix, economic nexus threshold monitoring, VAT/GST filing schedules, and cross-border tax compliance."
          icon={Building}
          statusBadge="● TAX COMPLIANCE FEED LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TAX JURISDICTIONS" value={`${MOCK_TAX_JURISDICTIONS.length}`} subtext="ACTIVE REGIONAL MATRICES" accentColor="text-blue-400" />
          <AGMetricCard label="NEXUS COMPLIANCE" value="100% MET" subtext="AUTOMATED NEXUS TRACKING" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG TAX RATE" value="13.63%" subtext="BLENDED JURISDICTION RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="FILING CADENCE" value="UP TO DATE" subtext="ZERO OVERDUE RETURNS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Jurisdiction ID, Region..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['JURISDICTIONS', 'NEXUS_THRESHOLDS', 'EXEMPTION_CERTIFICATES', 'CROSS_BORDER', 'AUDIT'] as TaxJurisdictionsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'JURISDICTIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">JURISDICTION ID</th>
                  <th className="p-3">REGION NAME</th>
                  <th className="p-3">TAX TYPE</th>
                  <th className="p-3">STANDARD RATE</th>
                  <th className="p-3">NEXUS STATUS</th>
                  <th className="p-3">FILING CADENCE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{t.jurisdictionId}</td>
                    <td className="p-3 font-bold text-slate-200">{t.regionName}</td>
                    <td className="p-3 font-bold text-purple-400">{t.taxType}</td>
                    <td className="p-3 font-bold text-emerald-400">{t.standardRate}</td>
                    <td className="p-3 text-emerald-400 font-bold">{t.economicNexusMet ? 'NEXUS MET' : 'NO NEXUS'}</td>
                    <td className="p-3 text-slate-300 font-mono">{t.filingCadence}</td>
                    <td className="p-3"><AGBadge status={t.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'JURISDICTIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
