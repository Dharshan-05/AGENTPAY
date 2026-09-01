'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { TransactionHeader } from '@/components/transactions/transaction-header';
import { TransactionMetrics } from '@/components/transactions/transaction-metrics';
import { TransactionControls } from '@/components/transactions/transaction-controls';
import { TransactionTabs } from '@/components/transactions/transaction-tabs';
import { TransactionRegistry } from '@/components/transactions/transaction-registry';
import { PaymentIntentsView } from '@/components/transactions/payment-intents';
import { TransactionLifecycle } from '@/components/transactions/transaction-lifecycle';
import { TransactionRefunds } from '@/components/transactions/transaction-refunds';
import { TransactionEvents } from '@/components/transactions/transaction-events';
import { TransactionAudit } from '@/components/transactions/transaction-audit';
import { TransactionInspector } from '@/components/transactions/transaction-inspector';

import {
  TxnTabType, TxnRecord, TxnFilterState, TxnInspectorDetail
} from '@/components/transactions/transaction-types';

import {
  PRODUCTION_TRANSACTIONS,
  PRODUCTION_INTENTS,
  PRODUCTION_REFUNDS,
  PRODUCTION_EVENTS,
  PRODUCTION_AUDIT,
  PRODUCTION_LIFECYCLE_SETTLED,
  PRODUCTION_LIFECYCLE_BLOCKED,
  MOCK_TXN_DETAIL
} from '@/components/transactions/transaction-data';

import { useTransactions } from '@/lib/hooks/useTransactions';
import { getSharedCommerceState } from '@/lib/commerce-store';
import { useEffect } from 'react';

export default function TransactionOperationsPage() {
  const { createPurchaseRequest, validatePurchaseRequest, executePurchaseRequest } = useTransactions();

  const [activeTab, setActiveTab] = useState<TxnTabType>('REGISTRY');
  const [selectedLifecycle, setSelectedLifecycle] = useState<'SETTLED' | 'BLOCKED'>('SETTLED');
  const [selectedTxn, setSelectedTxn] = useState<TxnInspectorDetail | null>(null);
  const [sharedState, setSharedState] = useState<any>(null);

  useEffect(() => {
    setSharedState(getSharedCommerceState());
    const handleUpdate = () => {
      setSharedState(getSharedCommerceState());
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('agentpay_commerce_session_updated', handleUpdate);
      return () => window.removeEventListener('agentpay_commerce_session_updated', handleUpdate);
    }
  }, []);

  const [filters, setFilters] = useState<TxnFilterState>({
    searchQuery: '',
    status: 'ALL',
    processor: 'ALL',
    paymentMethod: 'ALL',
    riskTier: 'ALL',
    agent: 'ALL',
    environment: 'ALL',
    dateRange: 'ALL',
  });

  const allTransactions = useMemo(() => {
    if (sharedState?.selected_product) {
      const formattedPrice = `₹${Number(sharedState.current_price || sharedState.selected_product.price).toLocaleString('en-IN')}`;
      const dynamicTxn: TxnRecord = {
        id: 'txn_dyn_1',
        transactionId: sharedState.razorpay_order_id ? `TXN-${sharedState.razorpay_order_id.slice(-8).toUpperCase()}` : `TXN-SESSION-001`,
        paymentIntentId: sharedState.razorpay_payment_id || `PI-LIVE-001`,
        agentId: '00000000-0000-0000-0000-000000000002',
        agentName: 'Commerce Agent #002',
        merchant: sharedState.selected_product.seller?.seller_name || 'Appario Retail',
        customer: 'OPERATOR_PRIMARY',
        requestedAmount: formattedPrice,
        authorizedAmount: formattedPrice,
        capturedAmount: formattedPrice,
        netAmount: formattedPrice,
        fees: '₹0.00',
        currency: 'INR',
        paymentMethod: 'CARD',
        paymentMethodDetail: 'Razorpay Test Gateway Card',
        processor: 'RAZORPAY_TEST',
        processorReference: sharedState.razorpay_payment_id || 'pay_test_active',
        status: sharedState.purchase_state === 'PAYMENT_SUCCESSFUL' ? 'SETTLED' : (sharedState.purchase_state === 'BLOCKED' ? 'BLOCKED' : 'PENDING'),
        riskScore: sharedState.fraudguard_result?.fraudguard_risk_score || 5,
        riskTier: (sharedState.fraudguard_result?.fraudguard_risk_level?.toUpperCase() as any) || 'LOW',
        policyId: 'POL-AGP-COMMERCE-001',
        policyName: 'Autonomous Commerce Policy',
        policyDecision: sharedState.purchase_state === 'BLOCKED' ? 'BLOCKED' : 'APPROVED',
        requiresHumanApproval: true,
        environment: 'PRODUCTION',
        region: 'AP_SOUTH_1',
        responseCode: '200_SUCCESS',
        attemptCount: 1,
        createdAt: sharedState.updated_at || new Date().toISOString(),
        updatedAt: sharedState.updated_at || new Date().toISOString(),
      };
      return [dynamicTxn, ...PRODUCTION_TRANSACTIONS];
    }
    return PRODUCTION_TRANSACTIONS;
  }, [sharedState]);

  const filteredTransactions = useMemo(() => {
    return allTransactions.filter((txn) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        txn.transactionId.toLowerCase().includes(q) ||
        txn.paymentIntentId.toLowerCase().includes(q) ||
        txn.agentId.toLowerCase().includes(q) ||
        txn.agentName.toLowerCase().includes(q) ||
        txn.merchant.toLowerCase().includes(q) ||
        txn.processor.toLowerCase().includes(q) ||
        txn.processorReference.toLowerCase().includes(q) ||
        txn.policyId.toLowerCase().includes(q);
      const matchStatus = filters.status === 'ALL' || txn.status === filters.status;
      const matchProcessor = filters.processor === 'ALL' || txn.processor.toUpperCase() === filters.processor.toUpperCase().replace(' ', '_');
      const matchMethod = filters.paymentMethod === 'ALL' || txn.paymentMethod === filters.paymentMethod.replace(' ', '_');
      const matchRisk = filters.riskTier === 'ALL' || txn.riskTier === filters.riskTier;
      const matchAgent = filters.agent === 'ALL' || txn.agentId === filters.agent;
      const matchEnv = filters.environment === 'ALL' || txn.environment === filters.environment;
      return matchSearch && matchStatus && matchProcessor && matchMethod && matchRisk && matchAgent && matchEnv;
    });
  }, [allTransactions, filters]);

  const handleSelectTxn = (txn: TxnRecord) => {
    if (txn.transactionId === 'TXN-AGP-91F2') {
      setSelectedTxn(MOCK_TXN_DETAIL);
    } else {
      const detail: TxnInspectorDetail = {
        ...txn,
        lifecycle: txn.status === 'BLOCKED' ? PRODUCTION_LIFECYCLE_BLOCKED : PRODUCTION_LIFECYCLE_SETTLED,
        refunds: PRODUCTION_REFUNDS.filter(r => r.transactionId === txn.transactionId),
        events: PRODUCTION_EVENTS.filter(e => e.transactionId === txn.transactionId),
      };
      setSelectedTxn(detail);
    }
  };

  const handleReset = () => {
    setFilters({
      searchQuery: '', status: 'ALL', processor: 'ALL',
      paymentMethod: 'ALL', riskTier: 'ALL', agent: 'ALL',
      environment: 'ALL', dateRange: 'ALL',
    });
  };

  const blockedCount = PRODUCTION_TRANSACTIONS.filter(t => t.status === 'BLOCKED' || t.status === 'FAILED').length;

  const handleExportTransactions = () => {
    const headers = ['Transaction ID', 'Payment Intent ID', 'Agent Name', 'Merchant', 'Requested Amount', 'Status', 'Risk Score', 'Processor', 'Created At'];
    const rows = filteredTransactions.map(t => [
      t.transactionId,
      t.paymentIntentId,
      `"${t.agentName}"`,
      `"${t.merchant}"`,
      `"${t.requestedAmount}"`,
      t.status,
      t.riskScore,
      t.processor,
      `"${t.createdAt}"`
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `agentpay_transactions_export_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleRefreshTransactions = () => {
    setSharedState(getSharedCommerceState());
  };

  return (
    <AgentPayShell activeTab="transactions">
      <div className="space-y-6 pb-12">

        {/* HEADER */}
        <TransactionHeader
          onRefresh={handleRefreshTransactions}
          onExport={handleExportTransactions}
        />

        {/* METRICS */}
        <TransactionMetrics
          intentCount={PRODUCTION_INTENTS.length}
          txnCount={PRODUCTION_TRANSACTIONS.length}
          failedCount={blockedCount}
          refundCount={PRODUCTION_REFUNDS.length}
        />

        {/* CONTROLS */}
        <TransactionControls
          searchQuery={filters.searchQuery}
          onSearchChange={(v) => setFilters(f => ({ ...f, searchQuery: v }))}
          selectedStatus={filters.status}
          onStatusChange={(v) => setFilters(f => ({ ...f, status: v }))}
          selectedProcessor={filters.processor}
          onProcessorChange={(v) => setFilters(f => ({ ...f, processor: v }))}
          selectedMethod={filters.paymentMethod}
          onMethodChange={(v) => setFilters(f => ({ ...f, paymentMethod: v }))}
          selectedRisk={filters.riskTier}
          onRiskChange={(v) => setFilters(f => ({ ...f, riskTier: v }))}
          selectedAgent={filters.agent}
          onAgentChange={(v) => setFilters(f => ({ ...f, agent: v }))}
          selectedEnvironment={filters.environment}
          onEnvironmentChange={(v) => setFilters(f => ({ ...f, environment: v }))}
          selectedDate={filters.dateRange}
          onDateChange={(v) => setFilters(f => ({ ...f, dateRange: v }))}
          onReset={handleReset}
        />

        {/* TABS */}
        <TransactionTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          registryCount={filteredTransactions.length}
          intentCount={PRODUCTION_INTENTS.length}
          refundCount={PRODUCTION_REFUNDS.length}
          eventCount={PRODUCTION_EVENTS.length}
          auditCount={PRODUCTION_AUDIT.length}
        />

        {/* TAB CONTENT */}
        {activeTab === 'REGISTRY' && (
          <TransactionRegistry
            transactions={filteredTransactions}
            onSelect={handleSelectTxn}
          />
        )}

        {activeTab === 'INTENTS' && (
          <PaymentIntentsView intents={PRODUCTION_INTENTS} />
        )}

        {activeTab === 'LIFECYCLE' && (
          <TransactionLifecycle
            selectedLifecycle={selectedLifecycle}
            onLifecycleChange={setSelectedLifecycle}
          />
        )}

        {activeTab === 'REFUNDS' && (
          <TransactionRefunds refunds={PRODUCTION_REFUNDS} />
        )}

        {activeTab === 'EVENTS' && (
          <TransactionEvents events={PRODUCTION_EVENTS} />
        )}

        {activeTab === 'AUDIT' && (
          <TransactionAudit entries={PRODUCTION_AUDIT} />
        )}

        {/* INSPECTOR DRAWER */}
        <TransactionInspector
          txn={selectedTxn}
          onClose={() => setSelectedTxn(null)}
        />

      </div>
    </AgentPayShell>
  );
}
