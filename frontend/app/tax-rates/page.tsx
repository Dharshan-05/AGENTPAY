'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Building, RefreshCw } from 'lucide-react';
import { TaxRatesTabType } from '@/components/tax-rates/tax-rate-types';
import { MOCK_TAX_RATES } from '@/components/tax-rates/tax-rate-data';

export default function TaxRatesPage() {
  const [activeTab, setActiveTab] = useState<TaxRatesTabType>('RATES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_TAX_RATES.filter(t => 
      !search || t.taxRateId.toLowerCase().includes(search.toLowerCase()) || t.jurisdiction.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="tax-rates">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="JURISDICTION TAX RATE MATRIX & NEXUS CONTROL PLANE"
          title="TAX RATE"
          highlightTitle="MATRICES"
          description="Global tax rate jurisdiction matrix, economic nexus threshold tracking, VAT/GST rate rules, and tax compliance audit."
          icon={Building}
          statusBadge="● TAX RATE FEED ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="TAX MATRICES" value={`${MOCK_TAX_RATES.length}`} subtext="ACTIVE JURISDICTIONS" accentColor="text-blue-400" />
          <AGMetricCard label="NEXUS STATES" value="02 Active" subtext="ECONOMIC NEXUS MET" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG TAX RATE" value="13.62%" subtext="GLOBAL AVERAGE RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="RATE ACCURACY" value="100%" subtext="AUTOMATED REAL-TIME SYNC" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Tax Rate ID, Jurisdiction..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['RATES', 'NEXUS_RULES', 'JURISDICTIONS', 'EXEMPTIONS', 'FILING_SCHEDULE', 'AUDIT'] as TaxRatesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'RATES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">TAX RATE ID</th>
                  <th className="p-3">JURISDICTION</th>
                  <th className="p-3">TAX TYPE</th>
                  <th className="p-3">RATE</th>
                  <th className="p-3">NEXUS STATUS</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{t.taxRateId}</td>
                    <td className="p-3 font-bold text-slate-200">{t.jurisdiction}</td>
                    <td className="p-3 font-bold text-purple-400">{t.taxType}</td>
                    <td className="p-3 font-bold text-emerald-400">{t.rate}</td>
                    <td className="p-3 text-slate-300 font-bold">{t.nexusStatus}</td>
                    <td className="p-3"><AGBadge status={t.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'RATES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
