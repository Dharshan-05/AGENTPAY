'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { FileText, RefreshCw, Download, Lock, ArrowRight } from 'lucide-react';
import { LedgerTabType, LedgerEntryRecord } from '@/components/ledger/ledger-types';
import { MOCK_LEDGER } from '@/components/ledger/ledger-data';

export default function LedgerPage() {
  const [activeTab, setActiveTab] = useState<LedgerTabType>('ENTRIES');
  const [search, setSearch] = useState('');
  const [selectedLed, setSelectedLed] = useState<LedgerEntryRecord | null>(null);

  const filtered = useMemo(() => {
    return MOCK_LEDGER.filter(l => 
      !search || l.entryId.toLowerCase().includes(search.toLowerCase()) || l.journalId.toLowerCase().includes(search.toLowerCase()) || l.accountName.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="ledger">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="IMMUTABLE DOUBLE-ENTRY GENERAL LEDGER"
          title="FINANCIAL LEDGER"
          highlightTitle="OPERATIONS"
          description="Double-entry accounting journal engine, SHA-256 cryptographic chain integrity, zero-variance reconciliation, and audit compliance."
          icon={FileText}
          statusBadge="● LEDGER CHAIN VERIFIED"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
              <AGButton variant="secondary" size="sm" onClick={() => alert('Exporting ledger...')}>EXPORT LEDGER</AGButton>
            </div>
          }
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <AGMetricCard label="LEDGER ENTRIES" value={`${MOCK_LEDGER.length}`} subtext="JOURNAL LINE ITEMS" accentColor="text-blue-400" />
          <AGMetricCard label="DEBIT BALANCE" value="$786,529.00" subtext="BALANCED DEBITS" accentColor="text-emerald-400" />
          <AGMetricCard label="CREDIT BALANCE" value="$786,529.00" subtext="BALANCED CREDITS" accentColor="text-emerald-400" />
          <AGMetricCard label="TRIAL BALANCE" value="0.00 VARIANCE" subtext="DOUBLE-ENTRY VALID" accentColor="text-emerald-400" />
          <AGMetricCard label="HASH CHAIN" value="VERIFIED" subtext="SHA-256 TAMPER EVIDENT" accentColor="text-purple-400" />
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search Entry ID, Journal ID, Account, Hash..."
            className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 placeholder-slate-600 focus:outline-none"
          />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400 hover:text-slate-200">RESET</button>
        </div>

        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['ENTRIES', 'ACCOUNTS', 'JOURNALS', 'TRANSACTIONS', 'SETTLEMENTS', 'RECONCILIATION', 'INTEGRITY', 'AUDIT'] as LedgerTabType[]).map(t => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'ENTRIES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">ENTRY ID</th>
                  <th className="p-3">JOURNAL ID</th>
                  <th className="p-3">ACCOUNT</th>
                  <th className="p-3">DEBIT</th>
                  <th className="p-3">CREDIT</th>
                  <th className="p-3">TXN REF</th>
                  <th className="p-3">TIMESTAMP</th>
                  <th className="p-3">CURRENT HASH</th>
                  <th className="p-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(l => (
                  <tr key={l.id} onClick={() => setSelectedLed(l)} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-purple-400">{l.entryId}</td>
                    <td className="p-3 font-bold text-blue-400">{l.journalId}</td>
                    <td className="p-3 text-slate-200 font-bold">{l.accountName}</td>
                    <td className="p-3 text-emerald-400 font-bold">{l.debit}</td>
                    <td className="p-3 text-blue-400 font-bold">{l.credit}</td>
                    <td className="p-3 text-slate-300">{l.transactionRef}</td>
                    <td className="p-3 text-slate-500">{l.timestamp}</td>
                    <td className="p-3 text-slate-500 font-mono text-[10px]">{l.currentHash}</td>
                    <td className="p-3 text-right"><button className="px-2 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-[10px]">INSPECT</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab !== 'ENTRIES' && (
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">
            {activeTab} OPERATIONAL VIEW ACTIVE — 3 CRYPTOGRAPHIC JOURNAL ENTRIES VERIFIED
          </div>
        )}

        {selectedLed && (
          <AGDrawer isOpen={!!selectedLed} onClose={() => setSelectedLed(null)} title={`LEDGER INSPECTOR: ${selectedLed.entryId}`} subtitle="CRYPTOGRAPHIC SHA-256 JOURNAL TRACE">
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/20 space-y-1">
                <div className="text-[9px] text-purple-400 font-bold uppercase flex items-center gap-1"><Lock className="w-3 h-3" /> HASH CHAIN LINK</div>
                <div className="flex items-center gap-1 text-[10px]">
                  <span className="text-slate-500">{selectedLed.prevHash.substring(0, 14)}...</span>
                  <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
                  <span className="text-purple-400 font-bold">{selectedLed.currentHash.substring(0, 14)}...</span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-white/[0.06] space-y-1">
                <div className="flex justify-between"><span className="text-slate-500">Account:</span><span className="text-slate-200 font-bold">{selectedLed.accountName}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Debit / Credit:</span><span className="text-emerald-400 font-bold">{selectedLed.debit} / {selectedLed.credit}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Integrity:</span><span className="text-emerald-400 font-bold">{selectedLed.integrityState}</span></div>
              </div>
            </div>
          </AGDrawer>
        )}
      </div>
    </AgentPayShell>
  );
}
