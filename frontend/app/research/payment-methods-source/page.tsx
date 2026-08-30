'use client';

import { useState, useMemo } from 'react';
import { SourceHeader } from '@/components/research/payment-methods/source-header';
import { SourceMetrics } from '@/components/research/payment-methods/source-metrics';
import { SourceControls } from '@/components/research/payment-methods/source-controls';
import { SourceTabs } from '@/components/research/payment-methods/source-tabs';
import { SourceRegistry } from '@/components/research/payment-methods/source-registry';
import { SourceMethodCatalog } from '@/components/research/payment-methods/source-method-catalog';
import { SourceCardsBanks } from '@/components/research/payment-methods/source-cards-banks';
import { SourceProcessorMatrix } from '@/components/research/payment-methods/source-processor-matrix';
import { SourceRouting } from '@/components/research/payment-methods/source-routing';
import { SourceSecurity } from '@/components/research/payment-methods/source-security';
import { SourceRisk } from '@/components/research/payment-methods/source-risk';
import { SourceAudit } from '@/components/research/payment-methods/source-audit';
import { SourceInspector } from '@/components/research/payment-methods/source-inspector';

import {
  PaymentMethodSourceTabType, PaymentInstrumentRecord, PaymentMethodFilterState
} from '@/components/research/payment-methods/source-types';

import {
  MOCK_SOURCE_INSTRUMENTS,
  MOCK_CATALOG_TYPES,
  MOCK_PROCESSOR_MATRIX,
  MOCK_ROUTING_DECISIONS,
  MOCK_SECURITY_RECORDS,
  MOCK_RISK_RECORDS,
  MOCK_SOURCE_AUDIT
} from '@/components/research/payment-methods/source-data';

import './payment-methods-source.css';

export default function PaymentMethodsSourceResearchPage() {
  const [activeTab, setActiveTab] = useState<PaymentMethodSourceTabType>('REGISTRY');
  const [selectedInstrument, setSelectedInstrument] = useState<PaymentInstrumentRecord | null>(null);

  const [filters, setFilters] = useState<PaymentMethodFilterState>({
    searchQuery: '',
    type: 'ALL',
    status: 'ALL',
    processor: 'ALL',
    agent: 'ALL',
    riskTier: 'ALL',
    environment: 'ALL',
    country: 'ALL',
    currency: 'ALL',
  });

  const filteredInstruments = useMemo(() => {
    return MOCK_SOURCE_INSTRUMENTS.filter((inst) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        inst.instrumentId.toLowerCase().includes(q) ||
        inst.name.toLowerCase().includes(q) ||
        inst.maskedIdentifier.toLowerCase().includes(q) ||
        inst.brandOrBank.toLowerCase().includes(q) ||
        inst.agentId.toLowerCase().includes(q) ||
        inst.owner.toLowerCase().includes(q) ||
        inst.tokenId.toLowerCase().includes(q);
      const matchType = filters.type === 'ALL' || inst.type === filters.type;
      const matchStatus = filters.status === 'ALL' || inst.status === filters.status;
      const matchProcessor = filters.processor === 'ALL' || inst.processor === filters.processor;
      const matchAgent = filters.agent === 'ALL' || inst.agentId === filters.agent;
      const matchRisk = filters.riskTier === 'ALL' || inst.riskTier === filters.riskTier;
      const matchEnv = filters.environment === 'ALL' || inst.environment === filters.environment;
      return matchSearch && matchType && matchStatus && matchProcessor && matchAgent && matchRisk && matchEnv;
    });
  }, [filters]);

  const handleReset = () => {
    setFilters({
      searchQuery: '', type: 'ALL', status: 'ALL',
      processor: 'ALL', agent: 'ALL', riskTier: 'ALL',
      environment: 'ALL', country: 'ALL', currency: 'ALL',
    });
  };

  const activeCount = MOCK_SOURCE_INSTRUMENTS.filter(i => i.status === 'ACTIVE' || i.status === 'VERIFIED').length;
  const verifiedCount = MOCK_SOURCE_INSTRUMENTS.filter(i => i.status === 'VERIFIED' || i.avsCvvResult === 'VERIFIED').length;
  const restrictedCount = MOCK_SOURCE_INSTRUMENTS.filter(i => i.status === 'RESTRICTED' || i.status === 'SUSPENDED' || i.status === 'REVOKED').length;
  const expiringCount = MOCK_SOURCE_INSTRUMENTS.filter(i => i.status === 'EXPIRING_SOON' || i.status === 'EXPIRED').length;

  return (
    <div className="payment-methods-source-root min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8 space-y-6 font-mono">

      {/* HEADER */}
      <SourceHeader
        onRefresh={() => alert('Payment instrument research baseline telemetry refreshed.')}
        onExport={() => alert('Exporting payment method research ledger...')}
      />

      {/* METRICS */}
      <SourceMetrics
        totalMethods={MOCK_SOURCE_INSTRUMENTS.length}
        activeMethods={activeCount}
        verifiedMethods={verifiedCount}
        processorCoverage="5 CONNECTORS"
        restrictedBlocked={restrictedCount}
        expiringExpired={expiringCount}
      />

      {/* CONTROLS */}
      <SourceControls
        searchQuery={filters.searchQuery}
        onSearchChange={(v) => setFilters(f => ({ ...f, searchQuery: v }))}
        selectedType={filters.type}
        onTypeChange={(v) => setFilters(f => ({ ...f, type: v }))}
        selectedStatus={filters.status}
        onStatusChange={(v) => setFilters(f => ({ ...f, status: v }))}
        selectedProcessor={filters.processor}
        onProcessorChange={(v) => setFilters(f => ({ ...f, processor: v }))}
        selectedAgent={filters.agent}
        onAgentChange={(v) => setFilters(f => ({ ...f, agent: v }))}
        selectedRiskTier={filters.riskTier}
        onRiskTierChange={(v) => setFilters(f => ({ ...f, riskTier: v }))}
        selectedEnvironment={filters.environment}
        onEnvironmentChange={(v) => setFilters(f => ({ ...f, environment: v }))}
        selectedCountry={filters.country}
        onCountryChange={(v) => setFilters(f => ({ ...f, country: v }))}
        selectedCurrency={filters.currency}
        onCurrencyChange={(v) => setFilters(f => ({ ...f, currency: v }))}
        onReset={handleReset}
      />

      {/* TABS */}
      <SourceTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        registryCount={filteredInstruments.length}
        catalogCount={MOCK_CATALOG_TYPES.length}
        cardsBanksCount={MOCK_SOURCE_INSTRUMENTS.filter(i => i.type.includes('CARD') || i.type.includes('BANK')).length}
        matrixCount={MOCK_PROCESSOR_MATRIX.length}
        routingCount={MOCK_ROUTING_DECISIONS.length}
        securityCount={MOCK_SECURITY_RECORDS.length}
        riskCount={MOCK_RISK_RECORDS.length}
        auditCount={MOCK_SOURCE_AUDIT.length}
      />

      {/* TAB CONTENT */}
      {activeTab === 'REGISTRY' && (
        <SourceRegistry
          instruments={filteredInstruments}
          onSelect={setSelectedInstrument}
        />
      )}

      {activeTab === 'CATALOG' && (
        <SourceMethodCatalog types={MOCK_CATALOG_TYPES} />
      )}

      {activeTab === 'CARDS_BANKS' && (
        <SourceCardsBanks
          instruments={filteredInstruments}
          onSelect={setSelectedInstrument}
        />
      )}

      {activeTab === 'MATRIX' && (
        <SourceProcessorMatrix records={MOCK_PROCESSOR_MATRIX} />
      )}

      {activeTab === 'ROUTING' && (
        <SourceRouting decisions={MOCK_ROUTING_DECISIONS} />
      )}

      {activeTab === 'SECURITY' && (
        <SourceSecurity records={MOCK_SECURITY_RECORDS} />
      )}

      {activeTab === 'RISK' && (
        <SourceRisk records={MOCK_RISK_RECORDS} />
      )}

      {activeTab === 'AUDIT' && (
        <SourceAudit entries={MOCK_SOURCE_AUDIT} />
      )}

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        item={selectedInstrument}
        onClose={() => setSelectedInstrument(null)}
      />

    </div>
  );
}
