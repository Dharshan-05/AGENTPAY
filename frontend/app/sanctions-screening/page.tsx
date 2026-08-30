'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Shield, RefreshCw } from 'lucide-react';
import { SanctionsScreeningTabType } from '@/components/sanctions-screening/sanctions-screening-types';
import { MOCK_SANCTIONS_SCREENINGS } from '@/components/sanctions-screening/sanctions-screening-data';

export default function SanctionsScreeningPage() {
  const [activeTab, setActiveTab] = useState<SanctionsScreeningTabType>('SANCTIONS_MATCHES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SANCTIONS_SCREENINGS.filter(s => 
      !search || s.screeningId.toLowerCase().includes(search.toLowerCase()) || s.entityName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="sanctions-screening">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AML / OFAC SANCTIONS & FUZZY MATCHING CONTROL PLANE"
          title="SANCTIONS & AML"
          highlightTitle="SCREENING"
          description="OFAC Specially Designated Nationals (SDN) screening, UN/EU consolidated sanctions matching, fuzzy string algorithm verification, and AML enforcement."
          icon={Shield}
          statusBadge="● AML SANCTIONS FEED LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SCREENED ENTITIES" value={`${MOCK_SANCTIONS_SCREENINGS.length}`} subtext="PROCESSED SCREENINGS" accentColor="text-blue-400" />
          <AGMetricCard label="SANCTIONS MATCH RATE" value="0.00% MATCH" subtext="100% CLEAR PASS" accentColor="text-emerald-400" />
          <AGMetricCard label="OFAC FEED LATENCY" value="Real-Time" subtext="AUTOMATED LIST SYNC" accentColor="text-emerald-400" />
          <AGMetricCard label="FUZZY THRESHOLD" value="85% JARO-WINKLER" subtext="HIGH SENSITIVITY" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Screening ID, Entity Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['SANCTIONS_MATCHES', 'OFAC_LISTS', 'FUZZY_MATCHING', 'BLOCKLISTS', 'AUDIT'] as SanctionsScreeningTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'SANCTIONS_MATCHES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SCREENING ID</th>
                  <th className="p-3">ENTITY NAME</th>
                  <th className="p-3">MATCHED LIST</th>
                  <th className="p-3">FUZZY SCORE</th>
                  <th className="p-3">DECISION</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.screeningId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.entityName}</td>
                    <td className="p-3 font-mono text-purple-400">{s.matchedList}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.fuzzyMatchScore}</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.decision}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'SANCTIONS_MATCHES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
