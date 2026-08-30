'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Building, RefreshCw } from 'lucide-react';
import { TaxesTabType } from '@/components/taxes/tax-types';
import { MOCK_TAXES } from '@/components/taxes/tax-data';

export default function TaxesPage() {
  const [activeTab, setActiveTab] = useState<TaxesTabType>('JURISDICTIONS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TAXES.filter(t => 
      !search || t.taxId.toLowerCase().includes(search.toLowerCase()) || t.jurisdiction.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="taxes">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="GLOBAL TAX, VAT & CROSS-BORDER COMPLIANCE PLANE"
          title="TAX &"
          highlightTitle="COMPLIANCE"
          description="Automated cross-border VAT/GST tax calculation, US state sales tax nexus tracking, tax exemption certificates, and remittance filing."
          icon={Building}
          statusBadge="● TAX ENGINE ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="JURISDICTIONS" value={`${MOCK_TAXES.length}`} subtext="ACTIVE TAX NEXUS" accentColor="text-blue-400" />
          <AGMetricCard label="TAX COLLECTED" value="$98,076.60" subtext="TOTAL TAXES ACCRUED" accentColor="text-emerald-400" />
          <AGMetricCard label="EU VAT REMITTED" value="€96,691.00" subtext="Q2 FILING COMPLETE" accentColor="text-emerald-400" />
          <AGMetricCard label="EXEMPT CERTIFICATES" value="12 Valid" subtext="ZERO AUDIT GAPS" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Tax ID, Jurisdiction..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['JURISDICTIONS', 'CALCULATIONS', 'EXEMPTIONS', 'VAT_GST', 'RETURNS', 'REPORTS', 'AUDIT'] as TaxesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'JURISDICTIONS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">TAX ID</th>
                  <th className="p-3">JURISDICTION</th>
                  <th className="p-3">TAX TYPE</th>
                  <th className="p-3">RATE</th>
                  <th className="p-3">COLLECTED</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{t.taxId}</td>
                    <td className="p-3 font-bold text-slate-200">{t.jurisdiction}</td>
                    <td className="p-3 font-bold text-purple-400">{t.taxType}</td>
                    <td className="p-3 text-slate-300 font-bold">{t.taxRate}</td>
                    <td className="p-3 font-bold text-emerald-400">{t.taxCollected}</td>
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
