'use client';

import { useState, useMemo } from 'react';
import './transactions-source.css';

// Components
import { SourceHeader } from '@/components/research/transactions/source-header';
import { SourceMetrics } from '@/components/research/transactions/source-metrics';
import { SourceControls } from '@/components/research/transactions/source-controls';
import { SourceTabs } from '@/components/research/transactions/source-tabs';
import { SourceTransactionRegistry } from '@/components/research/transactions/source-transaction-registry';
import { SourcePaymentIntents } from '@/components/research/transactions/source-payment-intents';
import { SourceTransactionLifecycle } from '@/components/research/transactions/source-transaction-lifecycle';
import { SourceRefunds } from '@/components/research/transactions/source-refunds';
import { SourceTransactionEvents } from '@/components/research/transactions/source-transaction-events';
import { SourceAuditTrail } from '@/components/research/transactions/source-audit-trail';
import { SourceInspector } from '@/components/research/transactions/source-inspector';

// Types
import {
  TransactionSourceTabType,
  SourceTransactionRecord,
} from '@/components/research/transactions/source-types';

// Data
import {
  MOCK_SOURCE_TRANSACTIONS,
  MOCK_SOURCE_INTENTS,
  MOCK_SOURCE_REFUNDS,
  MOCK_SOURCE_EVENTS,
  MOCK_TXN_DETAIL_91F2,
  MOCK_LIFECYCLE_SETTLED,
  MOCK_LIFECYCLE_BLOCKED,
} from '@/components/research/transactions/source-data';

export default function TransactionOperationsSourceResearchPage() {
  // ---- TAB STATE ----
  const [activeTab, setActiveTab] = useState<TransactionSourceTabType>('REGISTRY');

  // ---- FILTER STATE ----
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProcessor, setSelectedProcessor] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('ALL');
  const [selectedRiskTier, setSelectedRiskTier] = useState('ALL');
  const [selectedAgent, setSelectedAgent] = useState('ALL');
  const [selectedEnvironment, setSelectedEnvironment] = useState('ALL');

  // ---- INSPECTOR STATE ----
  const [selectedTransaction, setSelectedTransaction] = useState<SourceTransactionRecord | null>(null);

  // ---- LIFECYCLE TAB STATE ----
  const [selectedLifecycleId, setSelectedLifecycleId] = useState<string>('TXN-AGP-91F2');

  // ---- FILTERED TRANSACTIONS ----
  const filteredTransactions = useMemo(() => {
    return MOCK_SOURCE_TRANSACTIONS.filter((t) => {
      const q = searchQuery.toLowerCase();
      const matchSearch =
        !q ||
        t.transactionId.toLowerCase().includes(q) ||
        t.paymentIntentId.toLowerCase().includes(q) ||
        t.agentId.toLowerCase().includes(q) ||
        t.agentName.toLowerCase().includes(q) ||
        t.merchant.toLowerCase().includes(q) ||
        t.customer.toLowerCase().includes(q) ||
        t.requestedAmount.toLowerCase().includes(q) ||
        t.processor.toLowerCase().includes(q);

      const matchProcessor = selectedProcessor === 'ALL' || t.processor.toLowerCase().includes(selectedProcessor.toLowerCase());
      const matchStatus = selectedStatus === 'ALL' || t.status === selectedStatus;
      const matchMethod = selectedPaymentMethod === 'ALL' || t.paymentMethod === selectedPaymentMethod;
      const matchRisk = selectedRiskTier === 'ALL' || t.riskTier === selectedRiskTier;
      const matchAgent = selectedAgent === 'ALL' || t.agentId === selectedAgent;
      const matchEnv = selectedEnvironment === 'ALL' || t.environment === selectedEnvironment;

      return matchSearch && matchProcessor && matchStatus && matchMethod && matchRisk && matchAgent && matchEnv;
    });
  }, [searchQuery, selectedProcessor, selectedStatus, selectedPaymentMethod, selectedRiskTier, selectedAgent, selectedEnvironment]);

  // ---- RESET FILTERS ----
  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedProcessor('ALL');
    setSelectedStatus('ALL');
    setSelectedPaymentMethod('ALL');
    setSelectedRiskTier('ALL');
    setSelectedAgent('ALL');
    setSelectedEnvironment('ALL');
  };

  // ---- LIFECYCLE DATA ----
  const lifecycleSteps = selectedLifecycleId === 'TXN-AGP-91F2'
    ? MOCK_LIFECYCLE_SETTLED
    : MOCK_LIFECYCLE_BLOCKED;

  const lifecycleTxn = MOCK_SOURCE_TRANSACTIONS.find(t => t.transactionId === selectedLifecycleId);

  // ---- INSPECTOR DETAIL ----
  const inspectorDetail =
    selectedTransaction?.transactionId === 'TXN-AGP-91F2'
      ? MOCK_TXN_DETAIL_91F2
      : null;

  return (
    <div className="transactions-source-root min-h-screen bg-slate-100 font-sans">
      <div className="max-w-screen-2xl mx-auto p-4 sm:p-6 space-y-4">

        {/* HEADER */}
        <SourceHeader
          onRefresh={() => alert('Transaction feed refreshed')}
          onExport={() => alert('Exporting transaction ledger CSV')}
        />

        {/* METRICS */}
        <SourceMetrics />

        {/* CONTROLS */}
        <SourceControls
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedProcessor={selectedProcessor}
          onProcessorChange={setSelectedProcessor}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          selectedPaymentMethod={selectedPaymentMethod}
          onPaymentMethodChange={setSelectedPaymentMethod}
          selectedRiskTier={selectedRiskTier}
          onRiskTierChange={setSelectedRiskTier}
          selectedAgent={selectedAgent}
          onAgentChange={setSelectedAgent}
          selectedEnvironment={selectedEnvironment}
          onEnvironmentChange={setSelectedEnvironment}
          onReset={handleResetFilters}
        />

        {/* TABS */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm px-4 pt-3">
          <SourceTabs activeTab={activeTab} onTabChange={setActiveTab} />

          {/* TAB CONTENTS */}
          <div className="py-4">
            {activeTab === 'REGISTRY' && (
              <SourceTransactionRegistry
                transactions={filteredTransactions}
                onSelectTransaction={setSelectedTransaction}
                selectedId={selectedTransaction?.id}
              />
            )}

            {activeTab === 'INTENTS' && (
              <SourcePaymentIntents
                intents={MOCK_SOURCE_INTENTS}
                onSelectIntent={(pi) => {
                  const txn = MOCK_SOURCE_TRANSACTIONS.find(t => t.transactionId === pi.transactionId);
                  if (txn) setSelectedTransaction(txn);
                }}
              />
            )}

            {activeTab === 'LIFECYCLE' && (
              <div className="space-y-4">
                {/* Lifecycle selector */}
                <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs font-sans">
                  <span className="text-[10px] text-slate-400 uppercase font-bold">VIEW LIFECYCLE FOR:</span>
                  <button
                    onClick={() => setSelectedLifecycleId('TXN-AGP-91F2')}
                    className={`px-3 py-1.5 rounded-xl font-bold transition-colors ${
                      selectedLifecycleId === 'TXN-AGP-91F2'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    TXN-AGP-91F2 · SETTLED ✓
                  </button>
                  <button
                    onClick={() => setSelectedLifecycleId('TXN-AGP-11A8')}
                    className={`px-3 py-1.5 rounded-xl font-bold transition-colors ${
                      selectedLifecycleId === 'TXN-AGP-11A8'
                        ? 'bg-rose-600 text-white'
                        : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    TXN-AGP-11A8 · BLOCKED ✗
                  </button>
                  <span className="text-[10px] text-slate-400 italic ml-auto">
                    10-stage pipeline: Intent → Identity → Capability → Policy → Risk → Auth → Capture → Processor → Settlement → Audit
                  </span>
                </div>

                <SourceTransactionLifecycle
                  steps={lifecycleSteps}
                  transactionId={selectedLifecycleId}
                  transactionStatus={lifecycleTxn?.status || 'UNKNOWN'}
                />
              </div>
            )}

            {activeTab === 'REFUNDS' && (
              <SourceRefunds refunds={MOCK_SOURCE_REFUNDS} />
            )}

            {activeTab === 'EVENTS' && (
              <SourceTransactionEvents events={MOCK_SOURCE_EVENTS} />
            )}

            {activeTab === 'AUDIT' && (
              <SourceAuditTrail />
            )}
          </div>
        </div>

        {/* RESEARCH NOTES */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 text-xs font-sans space-y-3">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">PHASE 12A — RESEARCH NOTES & CROSS-MODULE MAP</div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-xl p-3 border border-blue-100">
              <div className="text-[9px] font-bold text-blue-600 uppercase mb-1">→ /agents</div>
              <div className="text-[10px] text-blue-800">Every transaction traces back to an originating agent via agentId. The inspector panel shows agent identity, policy binding, and risk posture.</div>
            </div>
            <div className="bg-violet-50 rounded-xl p-3 border border-violet-100">
              <div className="text-[9px] font-bold text-violet-600 uppercase mb-1">→ /agentguard</div>
              <div className="text-[10px] text-violet-800">Policy evaluation decisions (APPROVED / HITL_REVIEW / BLOCKED) connect directly to AGENTGUARD policy engine. Each transaction shows policyBinding + policyDecision.</div>
            </div>
            <div className="bg-rose-50 rounded-xl p-3 border border-rose-100">
              <div className="text-[9px] font-bold text-rose-600 uppercase mb-1">→ /fraudguard</div>
              <div className="text-[10px] text-rose-800">Risk scores, tiers, velocity flags, and geo-risk flags connect to FRAUDGUARD. High-risk transactions should surface on the FRAUDGUARD dashboard.</div>
            </div>
            <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-100">
              <div className="text-[9px] font-bold text-emerald-600 uppercase mb-1">→ /reconciliation</div>
              <div className="text-[10px] text-emerald-800">Settlement IDs and dispute IDs link directly to /reconciliation. Settled transactions carry settlementId references for batch matching.</div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
              <div className="text-[9px] font-bold text-slate-500 uppercase mb-1">TOP SOURCE #1</div>
              <div className="text-[10px] text-slate-700 font-bold">juspay/hyperswitch</div>
              <div className="text-[10px] text-slate-500">Best: Payment Intent lifecycle, multi-processor routing, attempt tracking</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
              <div className="text-[9px] font-bold text-slate-500 uppercase mb-1">TOP SOURCE #2</div>
              <div className="text-[10px] text-slate-700 font-bold">killbill/killbill (Kaui)</div>
              <div className="text-[10px] text-slate-500">Best: Audit trail design, payment state machine, account transaction history</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
              <div className="text-[9px] font-bold text-slate-500 uppercase mb-1">TOP SOURCE #3</div>
              <div className="text-[10px] text-slate-700 font-bold">getlago/lago</div>
              <div className="text-[10px] text-slate-500">Best: Financial event architecture, invoice/payment relationships, billing lifecycle</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
              <div className="text-[9px] font-bold text-slate-500 uppercase mb-1">TOP SOURCES #4-5</div>
              <div className="text-[10px] text-slate-700 font-bold">medusajs/medusa · apache/fineract</div>
              <div className="text-[10px] text-slate-500">Best: Capture/refund UX, payment sessions, double-entry financial concept</div>
            </div>
          </div>
        </div>

      </div>

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        transaction={selectedTransaction}
        detail={inspectorDetail}
        onClose={() => setSelectedTransaction(null)}
      />
    </div>
  );
}
