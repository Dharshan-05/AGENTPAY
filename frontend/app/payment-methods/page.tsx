'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PaymentMethodHeader } from '@/components/payment-methods/payment-method-header';
import { PaymentMethodMetrics } from '@/components/payment-methods/payment-method-metrics';
import { PaymentMethodControls } from '@/components/payment-methods/payment-method-controls';
import { PaymentMethodTabs } from '@/components/payment-methods/payment-method-tabs';
import { PaymentMethodRegistry } from '@/components/payment-methods/payment-method-registry';
import { PaymentMethodCatalog } from '@/components/payment-methods/payment-method-catalog';
import { PaymentMethodCardsBanks } from '@/components/payment-methods/payment-method-cards-banks';
import { PaymentMethodProcessors } from '@/components/payment-methods/payment-method-processors';
import { PaymentMethodRouting } from '@/components/payment-methods/payment-method-routing';
import { PaymentMethodSecurity } from '@/components/payment-methods/payment-method-security';
import { PaymentMethodRisk } from '@/components/payment-methods/payment-method-risk';
import { PaymentMethodAudit } from '@/components/payment-methods/payment-method-audit';
import { PaymentMethodInspector } from '@/components/payment-methods/payment-method-inspector';
import { RegisterPaymentMethodModal } from '@/components/payment-methods/register-payment-method-modal';

import {
  PaymentMethodTabType, PaymentInstrumentRecord, PaymentMethodFilterState, InstrumentType
} from '@/components/payment-methods/payment-method-types';

import {
  PRODUCTION_INSTRUMENTS,
  PRODUCTION_CATALOG_TYPES,
  PRODUCTION_PROCESSOR_MATRIX,
  PRODUCTION_ROUTING_DECISIONS,
  PRODUCTION_SECURITY_RECORDS,
  PRODUCTION_RISK_RECORDS,
  PRODUCTION_AUDIT_LOG
} from '@/components/payment-methods/payment-method-data';

export default function PaymentMethodsProductionPage() {
  const [instruments, setInstruments] = useState<PaymentInstrumentRecord[]>(PRODUCTION_INSTRUMENTS);
  const [activeTab, setActiveTab] = useState<PaymentMethodTabType>('REGISTRY');
  const [selectedInstrument, setSelectedInstrument] = useState<PaymentInstrumentRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
    return instruments.filter((inst) => {
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
  }, [instruments, filters]);

  const handleReset = () => {
    setFilters({
      searchQuery: '', type: 'ALL', status: 'ALL',
      processor: 'ALL', agent: 'ALL', riskTier: 'ALL',
      environment: 'ALL', country: 'ALL', currency: 'ALL',
    });
  };

  const handleAddMethod = (data: { name: string; type: InstrumentType; env: string; currency: string; country: string; agent: string; processor: string }) => {
    const nextNum = instruments.length + 1;
    const newId = `PM-AGP-${nextNum.toString().padStart(3, '0')}`;
    const newRecord: PaymentInstrumentRecord = {
      id: `pm_${nextNum}`,
      instrumentId: newId,
      type: data.type,
      name: data.name,
      maskedIdentifier: data.type.includes('CARD') ? 'VISA •••• 9900' : 'BANK •••• 8810',
      brandOrBank: 'Visa / Chase Bank',
      owner: 'Finance Ops',
      agentId: data.agent,
      agentName: 'Autonomous Payment Agent',
      policyId: 'AGP-GOV-001',
      policyName: 'Micro-Payment Policy',
      environment: data.env as any,
      status: 'ACTIVE',
      tokenStatus: 'NETWORK_TOKEN',
      tokenId: `tok_ntk_${nextNum}900`,
      expirationDate: '12/29',
      processor: data.processor,
      processorReference: `pm_ref_${nextNum}`,
      riskTier: 'LOW',
      riskScore: 10,
      threeDsStatus: 'READY',
      avsCvvResult: 'VERIFIED',
      currency: data.currency,
      country: data.country,
      spendLimit: '$10,000.00',
      lastUsedAt: 'Just now',
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().replace('T', ' ').substring(0, 19),
    };

    setInstruments(prev => [newRecord, ...prev]);
    setIsModalOpen(false);
    alert(`Success: Registered payment method ${newId} (${data.name})`);
  };

  const activeCount = instruments.filter(i => i.status === 'ACTIVE' || i.status === 'VERIFIED').length;
  const highRiskCount = instruments.filter(i => i.riskTier === 'HIGH' || i.riskTier === 'CRITICAL').length;
  const suspendedCount = instruments.filter(i => i.status === 'SUSPENDED' || i.status === 'REVOKED' || i.status === 'RESTRICTED').length;

  return (
    <AgentPayShell activeTab="payment-methods">
      <div className="space-y-6 pb-12 font-mono">

        {/* HEADER */}
        <PaymentMethodHeader
          onRefresh={() => alert('Payment method telemetry refreshed.')}
          onExport={() => alert('Exporting payment method ledger...')}
          onAddMethod={() => setIsModalOpen(true)}
        />

        {/* METRICS */}
        <PaymentMethodMetrics
          totalMethods={instruments.length}
          activeMethods={activeCount}
          methodsUsed24h={1842}
          authSuccessRate="99.41%"
          highRiskCount={highRiskCount}
          suspendedCount={suspendedCount}
        />

        {/* CONTROLS */}
        <PaymentMethodControls
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
        <PaymentMethodTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          registryCount={filteredInstruments.length}
          catalogCount={PRODUCTION_CATALOG_TYPES.length}
          cardsBanksCount={instruments.filter(i => i.type.includes('CARD') || i.type.includes('BANK')).length}
          processorsCount={PRODUCTION_PROCESSOR_MATRIX.length}
          routingCount={PRODUCTION_ROUTING_DECISIONS.length}
          securityCount={PRODUCTION_SECURITY_RECORDS.length}
          riskCount={PRODUCTION_RISK_RECORDS.length}
          auditCount={PRODUCTION_AUDIT_LOG.length}
        />

        {/* TAB CONTENT */}
        {activeTab === 'REGISTRY' && (
          <PaymentMethodRegistry
            instruments={filteredInstruments}
            onSelect={setSelectedInstrument}
          />
        )}

        {activeTab === 'CATALOG' && (
          <PaymentMethodCatalog types={PRODUCTION_CATALOG_TYPES} />
        )}

        {activeTab === 'CARDS_BANKS' && (
          <PaymentMethodCardsBanks
            instruments={filteredInstruments}
            onSelect={setSelectedInstrument}
          />
        )}

        {activeTab === 'PROCESSORS' && (
          <PaymentMethodProcessors records={PRODUCTION_PROCESSOR_MATRIX} />
        )}

        {activeTab === 'ROUTING' && (
          <PaymentMethodRouting decisions={PRODUCTION_ROUTING_DECISIONS} />
        )}

        {activeTab === 'SECURITY' && (
          <PaymentMethodSecurity records={PRODUCTION_SECURITY_RECORDS} />
        )}

        {activeTab === 'RISK' && (
          <PaymentMethodRisk records={PRODUCTION_RISK_RECORDS} />
        )}

        {activeTab === 'AUDIT' && (
          <PaymentMethodAudit entries={PRODUCTION_AUDIT_LOG} />
        )}

        {/* INSPECTOR DRAWER */}
        <PaymentMethodInspector
          item={selectedInstrument}
          onClose={() => setSelectedInstrument(null)}
        />

        {/* REGISTER MODAL */}
        <RegisterPaymentMethodModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onAdd={handleAddMethod}
        />

      </div>
    </AgentPayShell>
  );
}
