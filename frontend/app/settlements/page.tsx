'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { Landmark, RefreshCw, Download, ArrowRight } from 'lucide-react';
import { SettlementTabType, SettlementRecord } from '@/components/settlements/settlement-types';
import { MOCK_SETTLEMENTS } from '@/components/settlements/settlement-data';

export default function SettlementsPage() {
  const [activeTab, setActiveTab] = useState<SettlementTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedSet, setSelectedSet] = useState<SettlementRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_SETTLEMENTS.filter(s => 
      !search || s.settlementId.toLowerCase().includes(search.toLowerCase()) || s.batchId.toLowerCase().includes(search.toLowerCase()) || s.merchantId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="settlements">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="BATCH & CLEARING CONTROL PLANE"
          title="SETTLEMENT"
          highlightTitle="OPERATIONS"
          description="Batch clearing management, gross-to-net fee calculation, processor payout reconciliation, and immutable ledger journal posting."
          icon={Landmark}
          statusBadge="● SETTLEMENT ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="SETTLEMENT BATCHES" value={`${MOCK_SETTLEMENTS.length}`} subtext="DAILY CLEARING CYCLES" accentColor="text-emerald-400" />
          <AGMetricCard label="GROSS VOLUME" value="$1.43M" subtext="TOTAL CLEARED" accentColor="text-emerald-400" />
          <AGMetricCard label="NET SETTLED" value="$1.42M" subtext="NET AFTER PROCESSOR FEES" accentColor="text-emerald-400" />
          <AGMetricCard label="PROCESSOR FEES" value="$8,449.00" subtext="AVG 0.59% INTERCHANGE" accentColor="text-amber-400" />
          <AGMetricCard label="RECONCILED RATE" value="100.0%" subtext="ZERO VARIANCE" accentColor="text-blue-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Settlement ID, Batch ID, Merchant, Ledger Ref..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'BATCHES', 'PROCESSORS', 'MERCHANTS', 'RECONCILIATION', 'EXCEPTIONS', 'TIMELINE', 'AUDIT'] as SettlementTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'REGISTRY' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">SETTLEMENT ID</th>
                  <th className="p-3">BATCH ID</th>
                  <th className="p-3">MERCHANT ID</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3">GROSS AMOUNT</th>
                  <th className="p-3">FEES</th>
                  <th className="p-3">NET AMOUNT</th>
                  <th className="p-3">DATE</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(s => (
                  <tr key={s.id} onClick={() => setSelectedSet(s)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-emerald-400">{s.settlementId}</td>
                    <td className="p-3 font-bold text-blue-400">{s.batchId}</td>
                    <td className="p-3 text-slate-300">{s.merchantId}</td>
                    <td className="p-3 text-purple-400 font-bold">{s.processor}</td>
                    <td className="p-3 text-slate-200">{s.grossAmount}</td>
                    <td className="p-3 text-amber-400">{s.fees}</td>
                    <td className="p-3 font-bold text-emerald-400">{s.netAmount} ({s.currency})</td>
                    <td className="p-3 text-slate-400">{s.settlementDate}</td>
                    <td className="p-3"><AGBadge status={s.status} size="sm" /></td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 3 BATCH CYCLES MONITORED
          </div>
        )}

        {selectedSet && (
          <AGDrawer isOpen={!!selectedSet} onClose={() => setSelectedSet(null)} title={`SETTLEMENT INSPECTOR: ${selectedSet.settlementId}`} subtitle="CLEARING & LEDGER BINDING">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1">
                <div className="text-[9px] text-emerald-400 font-bold uppercase">LEDGER BINDING</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedSet.batchId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedSet.settlementId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedSet.ledgerRef}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Gross:</span><span className="text-slate-200">{selectedSet.grossAmount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Fees:</span><span className="text-amber-400">{selectedSet.fees}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Net Amount:</span><span className="text-emerald-400 font-bold">{selectedSet.netAmount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Ledger Reference:</span><span className="text-purple-400 font-bold">{selectedSet.ledgerRef}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
