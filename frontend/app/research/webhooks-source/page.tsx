'use client';

import { useState, useMemo } from 'react';
import { SourceHeader } from '@/components/research/webhooks/source-header';
import { SourceMetrics } from '@/components/research/webhooks/source-metrics';
import { SourceControls } from '@/components/research/webhooks/source-controls';
import { SourceTabs } from '@/components/research/webhooks/source-tabs';
import { SourceWebhookRegistry } from '@/components/research/webhooks/source-webhook-registry';
import { SourceEventCatalog } from '@/components/research/webhooks/source-event-catalog';
import { SourceDeliveryLog } from '@/components/research/webhooks/source-delivery-log';
import { SourceSubscriptions } from '@/components/research/webhooks/source-subscriptions';
import { SourceRetryView } from '@/components/research/webhooks/source-retry-view';
import { SourceSecurity } from '@/components/research/webhooks/source-security';
import { SourceAudit } from '@/components/research/webhooks/source-audit';
import { SourceInspector } from '@/components/research/webhooks/source-inspector';

import {
  WebhookSourceTabType, WebhookEndpoint, WebhookEventRecord,
  WebhookDeliveryRecord, WebhookRetrySchedule, WebhookFilterState
} from '@/components/research/webhooks/source-types';

import {
  MOCK_SOURCE_ENDPOINTS,
  MOCK_SOURCE_EVENTS,
  MOCK_SOURCE_DELIVERIES,
  MOCK_SOURCE_SUBSCRIPTIONS,
  MOCK_SOURCE_RETRIES,
  MOCK_SOURCE_SECURITY,
  MOCK_SOURCE_AUDIT
} from '@/components/research/webhooks/source-data';

import './webhooks-source.css';

export default function WebhooksSourceResearchPage() {
  const [activeTab, setActiveTab] = useState<WebhookSourceTabType>('REGISTRY');
  const [selectedDelivery, setSelectedDelivery] = useState<WebhookDeliveryRecord | null>(null);

  const [filters, setFilters] = useState<WebhookFilterState>({
    searchQuery: '',
    status: 'ALL',
    eventType: 'ALL',
    environment: 'ALL',
    httpStatus: 'ALL',
    endpoint: 'ALL',
    dateRange: 'ALL',
  });

  const filteredDeliveries = useMemo(() => {
    return MOCK_SOURCE_DELIVERIES.filter((dlv) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        dlv.deliveryId.toLowerCase().includes(q) ||
        dlv.eventId.toLowerCase().includes(q) ||
        dlv.eventType.toLowerCase().includes(q) ||
        dlv.endpointName.toLowerCase().includes(q) ||
        dlv.targetUrl.toLowerCase().includes(q) ||
        dlv.agentId.toLowerCase().includes(q);
      const matchStatus = filters.status === 'ALL' || dlv.status === filters.status;
      const matchEvent = filters.eventType === 'ALL' || dlv.eventType === filters.eventType;
      const matchEnv = filters.environment === 'ALL' || dlv.environment === filters.environment;
      const matchHttp = filters.httpStatus === 'ALL' || dlv.responseStatus.toString() === filters.httpStatus;
      const matchEndpoint = filters.endpoint === 'ALL' || dlv.endpointId === filters.endpoint;
      return matchSearch && matchStatus && matchEvent && matchEnv && matchHttp && matchEndpoint;
    });
  }, [filters]);

  const handleSelectEndpoint = (ep: WebhookEndpoint) => {
    const matched = MOCK_SOURCE_DELIVERIES.find(d => d.endpointId === ep.endpointId) || MOCK_SOURCE_DELIVERIES[0];
    setSelectedDelivery(matched);
  };

  const handleSelectEvent = (ev: WebhookEventRecord) => {
    const matched = MOCK_SOURCE_DELIVERIES.find(d => d.eventId === ev.eventId) || MOCK_SOURCE_DELIVERIES[0];
    setSelectedDelivery(matched);
  };

  const handleSelectDelivery = (dlv: WebhookDeliveryRecord) => {
    setSelectedDelivery(dlv);
  };

  const handleReplay = (deliveryId: string) => {
    alert(`Manual replay triggered for delivery ${deliveryId}. New attempt queued.`);
  };

  const handleReset = () => {
    setFilters({
      searchQuery: '', status: 'ALL', eventType: 'ALL',
      environment: 'ALL', httpStatus: 'ALL', endpoint: 'ALL',
      dateRange: 'ALL',
    });
  };

  const failedCount = MOCK_SOURCE_DELIVERIES.filter(d => d.status === 'FAILED' || d.status === 'EXHAUSTED' || d.status === 'RETRYING').length;

  return (
    <div className="webhooks-source-root min-h-screen bg-slate-100 p-6 md:p-8 space-y-6 font-sans">
      {/* HEADER */}
      <SourceHeader
        onRefresh={() => alert('Webhook event telemetry refreshed.')}
        onExport={() => alert('Exporting webhook delivery log...')}
      />

      {/* METRICS */}
      <SourceMetrics
        endpointsCount={MOCK_SOURCE_ENDPOINTS.length}
        activeCount={MOCK_SOURCE_ENDPOINTS.filter(e => e.status === 'HEALTHY' || e.status === 'ACTIVE').length}
        deliveries24h="142.8k"
        successRate="99.92%"
        p95Latency="142ms"
        failedRetryingCount={failedCount}
      />

      {/* CONTROLS */}
      <SourceControls
        searchQuery={filters.searchQuery}
        onSearchChange={(v) => setFilters(f => ({ ...f, searchQuery: v }))}
        selectedStatus={filters.status}
        onStatusChange={(v) => setFilters(f => ({ ...f, status: v }))}
        selectedEventType={filters.eventType}
        onEventTypeChange={(v) => setFilters(f => ({ ...f, eventType: v }))}
        selectedEnvironment={filters.environment}
        onEnvironmentChange={(v) => setFilters(f => ({ ...f, environment: v }))}
        selectedHttpStatus={filters.httpStatus}
        onHttpStatusChange={(v) => setFilters(f => ({ ...f, httpStatus: v }))}
        selectedEndpoint={filters.endpoint}
        onEndpointChange={(v) => setFilters(f => ({ ...f, endpoint: v }))}
        onReset={handleReset}
      />

      {/* TABS */}
      <SourceTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        endpointCount={MOCK_SOURCE_ENDPOINTS.length}
        eventCount={MOCK_SOURCE_EVENTS.length}
        deliveryCount={filteredDeliveries.length}
        subscriptionCount={MOCK_SOURCE_SUBSCRIPTIONS.length}
        retryCount={MOCK_SOURCE_RETRIES.length}
        auditCount={MOCK_SOURCE_AUDIT.length}
      />

      {/* TAB CONTENTS */}
      {activeTab === 'REGISTRY' && (
        <SourceWebhookRegistry
          endpoints={MOCK_SOURCE_ENDPOINTS}
          onSelect={handleSelectEndpoint}
        />
      )}

      {activeTab === 'EVENTS' && (
        <SourceEventCatalog
          events={MOCK_SOURCE_EVENTS}
          onSelect={handleSelectEvent}
        />
      )}

      {activeTab === 'DELIVERIES' && (
        <SourceDeliveryLog
          deliveries={filteredDeliveries}
          onSelect={handleSelectDelivery}
        />
      )}

      {activeTab === 'SUBSCRIPTIONS' && (
        <SourceSubscriptions subscriptions={MOCK_SOURCE_SUBSCRIPTIONS} />
      )}

      {activeTab === 'RETRIES' && (
        <SourceRetryView
          retries={MOCK_SOURCE_RETRIES}
          onReplay={(ret) => handleReplay(ret.deliveryId)}
        />
      )}

      {activeTab === 'SECURITY' && (
        <SourceSecurity records={MOCK_SOURCE_SECURITY} />
      )}

      {activeTab === 'AUDIT' && (
        <SourceAudit entries={MOCK_SOURCE_AUDIT} />
      )}

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        delivery={selectedDelivery}
        onClose={() => setSelectedDelivery(null)}
        onReplay={handleReplay}
      />
    </div>
  );
}
