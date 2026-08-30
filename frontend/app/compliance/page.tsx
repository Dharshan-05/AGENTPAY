'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { FileCheck, RefreshCw } from 'lucide-react';
import { ComplianceTabType } from '@/components/compliance/compliance-types';
import { MOCK_COMPLIANCE } from '@/components/compliance/compliance-data';

export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState<ComplianceTabType>('AML_SANCTIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_COMPLIANCE.filter(c => 
      !search || c.complianceId.toLowerCase().includes(search.toLowerCase()) || c.entityName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="compliance">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="AML, SANCTIONS & KYC COMPLIANCE GOVERNANCE PLANE"
          title="AML &"
          highlightTitle="COMPLIANCE"
          description="Automated OFAC/OFSI sanctions screening, KYC/KYB identity verification, PEP risk scoring, and regulatory reporting."
          icon={FileCheck}
          statusBadge="● COMPLIANCE SCREENING ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SANCTIONS CHECKS" value={`${MOCK_COMPLIANCE.length}`} subtext="ACTIVE SCREENING" accentColor="text-blue-400" />
          <AGMetricCard label="OFAC CLEARANCE" value="100%" subtext="ZERO SANCTION MATCHES" accentColor="text-emerald-400" />
          <AGMetricCard label="KYC PASS RATE" value="99.6%" subtext="AUTOMATED VERIFICATION" accentColor="text-emerald-400" />
          <AGMetricCard label="UNDER REVIEW" value="00" subtext="ZERO PENDING REVIEWS" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Compliance ID, Entity Name..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['AML_SANCTIONS', 'KYC_KYB', 'PEP_CHECKS', 'PEP_RESULTS', 'RISK_TIERS', 'REPORTS', 'AUDIT'] as ComplianceTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'AML_SANCTIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">COMPLIANCE ID</th>
                  <th className="p-3">ENTITY NAME</th>
                  <th className="p-3">ENTITY TYPE</th>
                  <th className="p-3">CHECK TYPE</th>
                  <th className="p-3">RISK SCORE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{c.complianceId}</td>
                    <td className="p-3 font-bold text-slate-200">{c.entityName}</td>
                    <td className="p-3 font-bold text-purple-400">{c.entityType}</td>
                    <td className="p-3 text-slate-300">{c.checkType}</td>
                    <td className="p-3 text-emerald-400 font-bold">{c.riskScore}/100</td>
                    <td className="p-3"><AGBadge status={c.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'AML_SANCTIONS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
