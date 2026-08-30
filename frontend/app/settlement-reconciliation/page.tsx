'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Landmark, RefreshCw } from 'lucide-react';
import { SettlementReconciliationTabType } from '@/components/settlement-reconciliation/settlement-reconciliation-types';
import { MOCK_SETTLEMENT_RECONCILIATION } from '@/components/settlement-reconciliation/settlement-reconciliation-data';

export default function SettlementReconciliationPage() {
  const [activeTab, setActiveTab] = useState<SettlementReconciliationTabType>('BATCHES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_SETTLEMENT_RECONCILIATION.filter(s => 
      !search || s.batchId.toLowerCase().includes(search.toLowerCase()) || s.processor.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="settlement-reconciliation">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="SETTLEMENT BATCH & DOUBLE-ENTRY RECONCILIATION PLANE"
          title="SETTLEMENT"
          highlightTitle="RECONCILIATION"
          description="Automated processor settlement batch matching, net fee deduction auditing, double-entry ledger verification, and zero-variance reconciliation."
          icon={Landmark}
          statusBadge="● RECONCILIATION ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="SETTLEMENT BATCHES" value={`${MOCK_SETTLEMENT_RECONCILIATION.length}`} subtext="RECONCILED BATCHES" accentColor="text-blue-400" />
          <AGMetricCard label="GROSS RECONCILED" value="$426.25K" subtext="PROCESSED SETTLEMENTS" accentColor="text-emerald-400" />
          <AGMetricCard label="TOTAL MATCHED TXNS" value="2,310 Txns" subtext="100% MATCHED TRANSACTIONS" accentColor="text-emerald-400" />
          <AGMetricCard label="RECON VARIANCE" value="$0.00 ZERO" subtext="PERFECT LEDGER MATCH" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Batch ID, Processor..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['BATCHES', 'MATCHED', 'DISCREPANCIES', 'BANK_FEEDS', 'FEE_DEDUCTIONS', 'AUDIT'] as SettlementReconciliationTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'BATCHES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">BATCH ID</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">GROSS AMOUNT</th>
                  <th className="p-3">FEES DEDUCTED</th>
                  <th className="p-3">NET SETTLED</th>
                  <th className="p-3">MATCHED TXNS</th>
                  <th className="p-3">VARIANCE</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{s.batchId}</td>
                    <td className="p-3 font-bold text-slate-200">{s.processor}</td>
                    <td className="p-3 text-slate-300">{s.grossAmount}</td>
                    <td className="p-3 text-amber-400">{s.feesDeducted}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.netSettled}</td>
                    <td className="p-3 text-slate-300 font-bold">{s.matchedTransactions} txns</td>
                    <td className="p-3 text-emerald-400 font-bold">{s.variance}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'BATCHES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
