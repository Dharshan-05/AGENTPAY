'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { FileCode, RefreshCw } from 'lucide-react';
import { LedgerAdjustmentLogsTabType } from '@/components/ledger-adjustment-logs/ledger-adjustment-log-types';
import { MOCK_LEDGER_ADJUSTMENTS } from '@/components/ledger-adjustment-logs/ledger-adjustment-log-data';

export default function LedgerAdjustmentLogsPage() {
  const [activeTab, setActiveTab] = useState<LedgerAdjustmentLogsTabType>('ADJUSTMENT_LOGS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_LEDGER_ADJUSTMENTS.filter(l => 
      !search || l.adjustmentId.toLowerCase().includes(search.toLowerCase()) || l.ledgerAccount.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="ledger-adjustment-logs">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="IMMUTABLE DOUBLE-ENTRY LEDGER ADJUSTMENT & EXCEPTION LOG PLANE"
          title="LEDGER ADJUSTMENT"
          highlightTitle="LOGS"
          description="Manual & automated double-entry ledger adjustment entries, multi-level supervisory approvals, fee rebalancing, and hash audit trail."
          icon={FileCode}
          statusBadge="● LEDGER ADJUSTMENT ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="POSTED ADJUSTMENTS" value={`${MOCK_LEDGER_ADJUSTMENTS.length}`} subtext="IMMUTABLE LEDGER ENTRIES" accentColor="text-blue-400" />
          <AGMetricCard label="TOTAL ADJUSTMENT VOL" value="$1,670.00" subtext="BALANCED DOUBLE-ENTRY" accentColor="text-emerald-400" />
          <AGMetricCard label="SUPERVISORY APPROVAL" value="100% VERIFIED" subtext="DUAL APPROVAL ENFORCED" accentColor="text-emerald-400" />
          <AGMetricCard label="AUDIT INTEGRITY" value="SHA-256 CHAIN" subtext="TAMPER-PROOF LEDGER" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Adjustment ID, Account..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ADJUSTMENT_LOGS', 'MANUAL_CORRECTIONS', 'RECONCILIATION_OFFSETS', 'AUDIT'] as LedgerAdjustmentLogsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'ADJUSTMENT_LOGS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ADJUSTMENT ID</th>
                  <th className="p-3">LEDGER ACCOUNT</th>
                  <th className="p-3">TYPE</th>
                  <th className="p-3">AMOUNT</th>
                  <th className="p-3">REASON CODE</th>
                  <th className="p-3">APPROVER REF</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(l => (
                  <tr key={l.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{l.adjustmentId}</td>
                    <td className="p-3 font-bold text-slate-200">{l.ledgerAccount}</td>
                    <td className="p-3 font-bold text-purple-400">{l.adjustmentType}</td>
                    <td className="p-3 font-bold text-emerald-400">{l.amount}</td>
                    <td className="p-3 text-slate-300 font-mono">{l.reasonCode}</td>
                    <td className="p-3 text-slate-400 font-mono">{l.approverRef}</td>
                    <td className="p-3"><AGBadge status={l.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'ADJUSTMENT_LOGS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
