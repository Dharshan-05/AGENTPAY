'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { RotateCcw, RefreshCw, Download, Plus, ArrowRight } from 'lucide-react';
import { RefundTabType, RefundRecord } from '@/components/refunds/refund-types';
import { MOCK_REFUNDS } from '@/components/refunds/refund-data';

export default function RefundsPage() {
  const [activeTab, setActiveTab] = useState<RefundTabType>('REGISTRY');
  const [search, setSearch] = useState('');
  const [selectedRef, setSelectedRef] = useState<RefundRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_REFUNDS.filter(r => 
      !search || r.refundId.toLowerCase().includes(search.toLowerCase()) || r.transactionId.toLowerCase().includes(search.toLowerCase()) || r.agentId.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="refunds">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="RETURN & REVERSAL CONTROL PLANE"
          title="REFUND"
          highlightTitle="OPERATIONS"
          description="Autonomous agent refund execution, partial and full reversals, processor settlement adjustments, and audit trail tracking."
          icon={RotateCcw}
          statusBadge="● REFUND ENGINE ONLINE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
              <AGButton variant="primary" size="sm" onClick={() => alert('Issue Refund Flow')}><Plus className="w-3.5 h-3.5 mr-1.5" /> ISSUE REFUND</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="TOTAL REFUNDS" value={`${MOCK_REFUNDS.length}`} subtext="PROCESSED REVERSALS" accentColor="text-purple-400" />
          <AGMetricCard label="REFUND VOLUME" value="$2,520.00" subtext="TOTAL REFUNDED" accentColor="text-purple-400" />
          <AGMetricCard label="SUCCEEDED" value="02" subtext="SETTLED REVERSALS" accentColor="text-emerald-400" />
          <AGMetricCard label="PROCESSING" value="01" subtext="IN-FLIGHT REFUND" accentColor="text-amber-400" />
          <AGMetricCard label="REFUND RATIO" value="0.14%" subtext="VS GROSS VOLUME" accentColor="text-blue-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Refund ID, Transaction ID, Agent, Reason..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['REGISTRY', 'REQUESTS', 'PROCESSING', 'PARTIAL_REFUNDS', 'FULL_REFUNDS', 'FAILED', 'AUDIT'] as RefundTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'}`}
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
                  <th className="p-3">REFUND ID</th>
                  <th className="p-3">TXN ID</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">REASON</th>
                  <th className="p-3">REQUESTED BY</th>
                  <th className="p-3">AGENT ID</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3">PROCESSOR</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(r => (
                  <tr key={r.id} onClick={() => setSelectedRef(r)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-purple-400">{r.refundId}</td>
                    <td className="p-3 font-bold text-blue-400">{r.transactionId}</td>
                    <td className="p-3 font-bold text-purple-300">{r.amount} ({r.currency})</td>
                    <td className="p-3 text-slate-300">{r.reason}</td>
                    <td className="p-3 text-slate-400">{r.requestedBy}</td>
                    <td className="p-3 font-bold text-blue-400">{r.agentId}</td>
                    <td className="p-3"><AGBadge status={r.status} size="sm" /></td>
                    <td className="p-3 text-slate-300">{r.processor}</td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'REGISTRY' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 3 REFUNDS MONITORED
          </div>
        )}

        {selectedRef && (
          <AGDrawer isOpen={!!selectedRef} onClose={() => setSelectedRef(null)} title={`REFUND INSPECTOR: ${selectedRef.refundId}`} subtitle="REFUND REVERSAL CONTROL">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/20 space-y-1">
                <div className="text-[9px] text-purple-400 font-bold uppercase">REVERSAL PATH</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-blue-400 font-bold">{selectedRef.transactionId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedRef.refundId}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-emerald-400 font-bold">{selectedRef.status}</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Refund Amount:</span><span className="text-purple-400 font-bold">{selectedRef.amount}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Reason:</span><span className="text-slate-200">{selectedRef.reason}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Requested By:</span><span className="text-slate-300">{selectedRef.requestedBy}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
