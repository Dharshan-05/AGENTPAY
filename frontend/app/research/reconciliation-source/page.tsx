'use client';

import { useState } from 'react';
import './reconciliation-source.css';
import { SourceHeader } from '@/components/research/reconciliation/source-header';
import { SourceMetrics } from '@/components/research/reconciliation/source-metrics';
import { SourceTabs } from '@/components/research/reconciliation/source-tabs';
import { SourceReconciliationTable } from '@/components/research/reconciliation/source-reconciliation-table';
import { SourceDisputesTable } from '@/components/research/reconciliation/source-disputes-table';
import { SourceInspector } from '@/components/research/reconciliation/source-inspector';

import {
  ReconciliationTabType,
  SourceSettlementBatch,
  SourceDisputeRecord,
} from '@/components/research/reconciliation/source-types';

import {
  MOCK_SETTLEMENT_BATCHES,
  MOCK_DISPUTES,
  MOCK_DISCREPANCIES,
  MOCK_AUDIT_LEDGER,
} from '@/components/research/reconciliation/source-data';

export default function ReconciliationSourceResearchPage() {
  const [activeTab, setActiveTab] = useState<ReconciliationTabType>('SETTLEMENTS');
  const [batches] = useState<SourceSettlementBatch[]>(MOCK_SETTLEMENT_BATCHES);
  const [disputes] = useState<SourceDisputeRecord[]>(MOCK_DISPUTES);

  // Inspector State
  const [selectedBatch, setSelectedBatch] = useState<SourceSettlementBatch | null>(null);
  const [selectedDispute, setSelectedDispute] = useState<SourceDisputeRecord | null>(null);

  return (
    <div className="reconciliation-source-root min-h-screen p-6 space-y-6 bg-slate-100 font-sans">
      
      {/* HEADER */}
      <SourceHeader
        onRefresh={() => alert('Feed refreshed')}
        onExport={() => alert('Exporting audit ledger')}
      />

      {/* METRICS */}
      <SourceMetrics />

      {/* TABS */}
      <SourceTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* TAB CONTENTS */}
      {activeTab === 'SETTLEMENTS' && (
        <SourceReconciliationTable
          batches={batches}
          onSelectBatch={(b) => setSelectedBatch(b)}
        />
      )}

      {activeTab === 'DISPUTES' && (
        <SourceDisputesTable
          disputes={disputes}
          onSelectDispute={(d) => setSelectedDispute(d)}
        />
      )}

      {activeTab === 'DISCREPANCIES' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
          <h3 className="font-bold text-slate-900 text-sm">Unresolved Gateway Discrepancies</h3>
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                  <th className="p-3">Batch & Txn ID</th>
                  <th className="p-3">Expected Amount</th>
                  <th className="p-3">Settled Amount</th>
                  <th className="p-3">Variance</th>
                  <th className="p-3">Variance Type</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {MOCK_DISCREPANCIES.map((disc) => (
                  <tr key={disc.id} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900">{disc.transactionId}</td>
                    <td className="p-3 font-bold text-slate-900">{disc.expectedAmount}</td>
                    <td className="p-3 font-bold text-emerald-600">{disc.settledAmount}</td>
                    <td className="p-3 font-bold text-rose-600">{disc.varianceAmount}</td>
                    <td className="p-3 text-slate-600 text-[10px]">{disc.varianceType}</td>
                    <td className="p-3 font-bold text-amber-600">{disc.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'AUDIT_TRAIL' && (
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
          <h3 className="font-bold text-slate-900 text-sm">Immutable Financial Audit Ledger</h3>
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                  <th className="p-3">Event ID & Actor</th>
                  <th className="p-3">Action Executed</th>
                  <th className="p-3">Amount</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Cryptographic Audit Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {MOCK_AUDIT_LEDGER.map((led) => (
                  <tr key={led.id} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-blue-700">{led.eventId}</td>
                    <td className="p-3 font-bold text-slate-900">{led.action}</td>
                    <td className="p-3 font-bold text-emerald-600">{led.amount}</td>
                    <td className="p-3 font-bold text-emerald-600">{led.status}</td>
                    <td className="p-3 text-slate-500 text-[10px] break-all">{led.hash}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        batchItem={selectedBatch}
        disputeItem={selectedDispute}
        onClose={() => {
          setSelectedBatch(null);
          setSelectedDispute(null);
        }}
      />

    </div>
  );
}
