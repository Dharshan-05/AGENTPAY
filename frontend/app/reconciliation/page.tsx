'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { ReconciliationHeader } from '@/components/reconciliation/reconciliation-header';
import { ReconciliationMetrics } from '@/components/reconciliation/reconciliation-metrics';
import { ReconciliationControls } from '@/components/reconciliation/reconciliation-controls';
import { ReconciliationTabs } from '@/components/reconciliation/reconciliation-tabs';
import { SettlementTable } from '@/components/reconciliation/settlement-table';
import { SettlementInspector } from '@/components/reconciliation/settlement-inspector';
import { DisputePipeline } from '@/components/reconciliation/dispute-pipeline';
import { DisputesTable } from '@/components/reconciliation/disputes-table';
import { DisputeInspector } from '@/components/reconciliation/dispute-inspector';
import { DiscrepanciesTable } from '@/components/reconciliation/discrepancies-table';
import { DiscrepancyInspector } from '@/components/reconciliation/discrepancy-inspector';
import { AuditLedger } from '@/components/reconciliation/audit-ledger';
import { AuditInspector } from '@/components/reconciliation/audit-inspector';

import {
  ReconciliationTabType,
  SettlementBatchRecord,
  DisputeRecord,
  DiscrepancyRecord,
  ReconciliationAuditEvent,
} from '@/components/reconciliation/reconciliation-types';

import {
  INITIAL_SETTLEMENT_BATCHES,
  INITIAL_DISPUTES,
  INITIAL_DISCREPANCIES,
  INITIAL_AUDIT_EVENTS,
} from '@/components/reconciliation/reconciliation-data';

export default function ProductionReconciliationPage() {
  const [activeTab, setActiveTab] = useState<ReconciliationTabType>('SETTLEMENTS');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProcessor, setSelectedProcessor] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedDateRange, setSelectedDateRange] = useState('24H');

  // State
  const [batches] = useState<SettlementBatchRecord[]>(INITIAL_SETTLEMENT_BATCHES);
  const [disputes] = useState<DisputeRecord[]>(INITIAL_DISPUTES);
  const [discrepancies] = useState<DiscrepancyRecord[]>(INITIAL_DISCREPANCIES);
  const [auditEvents] = useState<ReconciliationAuditEvent[]>(INITIAL_AUDIT_EVENTS);

  // Inspector State
  const [selectedBatch, setSelectedBatch] = useState<SettlementBatchRecord | null>(null);
  const [selectedDispute, setSelectedDispute] = useState<DisputeRecord | null>(null);
  const [selectedDiscrepancy, setSelectedDiscrepancy] = useState<DiscrepancyRecord | null>(null);
  const [selectedAuditEvent, setSelectedAuditEvent] = useState<ReconciliationAuditEvent | null>(null);

  // Filtered Datasets
  const filteredBatches = useMemo(() => {
    return batches.filter((b) => {
      const matchSearch =
        !searchQuery ||
        b.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.processor.toLowerCase().includes(searchQuery.toLowerCase());
      const matchProcessor = selectedProcessor === 'ALL' || b.processor.includes(selectedProcessor);
      const matchStatus = selectedStatus === 'ALL' || b.status === selectedStatus;
      return matchSearch && matchProcessor && matchStatus;
    });
  }, [batches, searchQuery, selectedProcessor, selectedStatus]);

  const filteredDisputes = useMemo(() => {
    return disputes.filter((d) => {
      const matchSearch =
        !searchQuery ||
        d.disputeId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.transactionId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.agentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.merchant.toLowerCase().includes(searchQuery.toLowerCase());
      return matchSearch;
    });
  }, [disputes, searchQuery]);

  const filteredDiscrepancies = useMemo(() => {
    return discrepancies.filter((d) => {
      const matchSearch =
        !searchQuery ||
        d.varianceId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.transactionId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.agentId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.processor.toLowerCase().includes(searchQuery.toLowerCase());
      const matchProcessor = selectedProcessor === 'ALL' || d.processor.includes(selectedProcessor);
      return matchSearch && matchProcessor;
    });
  }, [discrepancies, searchQuery, selectedProcessor]);

  const filteredAuditEvents = useMemo(() => {
    return auditEvents.filter((e) => {
      const matchSearch =
        !searchQuery ||
        e.eventId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.entity.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.action.toLowerCase().includes(searchQuery.toLowerCase());
      return matchSearch;
    });
  }, [auditEvents, searchQuery]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedProcessor('ALL');
    setSelectedStatus('ALL');
    setSelectedDateRange('24H');
  };

  return (
    <AgentPayShell activeTab="reconciliation">
      <div className="space-y-6 pb-12">
        
        {/* HEADER */}
        <ReconciliationHeader
          onRefresh={() => alert('Feed refreshed with live settlement telemetry')}
          onExport={() => alert('Exporting cryptographic audit ledger...')}
          onRunReconciliation={() => alert('Reconciliation matching pipeline triggered')}
        />

        {/* METRICS */}
        <ReconciliationMetrics
          totalSettled24h="$4.82M"
          activeDisputesCount={42}
          unresolvedVariancesCount={17}
          disputeWinRate="91.4%"
        />

        {/* CONTROLS & FILTERS */}
        <ReconciliationControls
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedProcessor={selectedProcessor}
          onProcessorChange={setSelectedProcessor}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          selectedDateRange={selectedDateRange}
          onDateRangeChange={setSelectedDateRange}
          onReset={handleResetFilters}
        />

        {/* TABS */}
        <ReconciliationTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* TAB 1: SETTLEMENTS */}
        {activeTab === 'SETTLEMENTS' && (
          <SettlementTable
            batches={filteredBatches}
            onSelectBatch={(b) => setSelectedBatch(b)}
          />
        )}

        {/* TAB 2: DISPUTES */}
        {activeTab === 'DISPUTES' && (
          <div className="space-y-6">
            <DisputePipeline />
            <DisputesTable
              disputes={filteredDisputes}
              onSelectDispute={(d) => setSelectedDispute(d)}
            />
          </div>
        )}

        {/* TAB 3: DISCREPANCIES */}
        {activeTab === 'DISCREPANCIES' && (
          <DiscrepanciesTable
            discrepancies={filteredDiscrepancies}
            onSelectDiscrepancy={(d) => setSelectedDiscrepancy(d)}
          />
        )}

        {/* TAB 4: AUDIT LEDGER */}
        {activeTab === 'AUDIT' && (
          <AuditLedger
            events={filteredAuditEvents}
            onSelectEvent={(e) => setSelectedAuditEvent(e)}
          />
        )}

        {/* SETTLEMENT INSPECTOR */}
        <SettlementInspector
          batch={selectedBatch}
          onClose={() => setSelectedBatch(null)}
        />

        {/* DISPUTE INSPECTOR */}
        <DisputeInspector
          dispute={selectedDispute}
          onClose={() => setSelectedDispute(null)}
        />

        {/* DISCREPANCY INSPECTOR */}
        <DiscrepancyInspector
          discrepancy={selectedDiscrepancy}
          onClose={() => setSelectedDiscrepancy(null)}
        />

        {/* AUDIT INSPECTOR */}
        <AuditInspector
          event={selectedAuditEvent}
          onClose={() => setSelectedAuditEvent(null)}
        />

      </div>
    </AgentPayShell>
  );
}
