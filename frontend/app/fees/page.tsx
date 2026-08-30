'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { Percent, RefreshCw } from 'lucide-react';
import { FeesTabType } from '@/components/fees/fee-types';
import { MOCK_FEES } from '@/components/fees/fee-data';

export default function FeesPage() {
  const [activeTab, setActiveTab] = useState<FeesTabType>('INTERCHANGE');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_FEES.filter(f => 
      !search || f.feeId.toLowerCase().includes(search.toLowerCase()) || f.transactionRef.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="fees">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="INTERCHANGE & NETWORK FEE OPERATIONS PLANE"
          title="FEE &"
          highlightTitle="COMMISSION"
          description="Interchange++ fee breakdown, card scheme network assessments, platform revenue margins, and processor fee reconciliation."
          icon={Percent}
          statusBadge="● FEE CALCULATOR ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="FEE RECORDS" value={`${MOCK_FEES.length}`} subtext="PROCESSED FEES" accentColor="text-blue-400" />
          <AGMetricCard label="EFFECTIVE FEE RATE" value="0.61%" subtext="AVG INTERCHANGE++ RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="PLATFORM MARGIN" value="$867.00" subtext="NET REVENUE MARGIN" accentColor="text-emerald-400" />
          <AGMetricCard label="INTERCHANGE ACCURACY" value="100%" subtext="ZERO VARIANCE MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Fee ID, Transaction Ref..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['INTERCHANGE', 'NETWORK_FEES', 'PLATFORM_MARGIN', 'SCHEME_FEES', 'PROCESSOR_SPLIT', 'RECONCILIATION', 'AUDIT'] as FeesTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'INTERCHANGE' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">FEE ID</th>
                  <th className="p-3">TXN REF</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">INTERCHANGE</th>
                  <th className="p-3">SCHEME FEE</th>
                  <th className="p-3">PLATFORM MARGIN</th>
                  <th className="p-3">TOTAL FEES</th>
                  <th className="p-3">EFFECTIVE RATE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(f => (
                  <tr key={f.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{f.feeId}</td>
                    <td className="p-3 font-bold text-purple-400">{f.transactionRef}</td>
                    <td className="p-3 text-slate-200">{f.processor}</td>
                    <td className="p-3 text-amber-400">{f.interchangeFee}</td>
                    <td className="p-3 text-amber-400">{f.schemeFee}</td>
                    <td className="p-3 font-bold text-emerald-400">{f.platformMargin}</td>
                    <td className="p-3 font-bold text-slate-100">{f.totalFees}</td>
                    <td className="p-3 font-bold text-emerald-400">{f.effectiveRate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'INTERCHANGE' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
