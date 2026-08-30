'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { WebhookHeader } from '@/components/webhooks/webhook-header';
import { WebhookMetrics } from '@/components/webhooks/webhook-metrics';
import { WebhookControls } from '@/components/webhooks/webhook-controls';
import { WebhookTabs } from '@/components/webhooks/webhook-tabs';
import { WebhookRegistry } from '@/components/webhooks/webhook-registry';
import { WebhookEvents } from '@/components/webhooks/webhook-events';
import { WebhookDeliveries } from '@/components/webhooks/webhook-deliveries';
import { WebhookSubscriptions } from '@/components/webhooks/webhook-subscriptions';
import { WebhookRetries } from '@/components/webhooks/webhook-retries';
import { WebhookSecurity } from '@/components/webhooks/webhook-security';
import { WebhookAudit } from '@/components/webhooks/webhook-audit';
import { WebhookInspector } from '@/components/webhooks/webhook-inspector';
import { RegisterWebhookModal } from '@/components/webhooks/register-webhook-modal';

import {
  WebhookTabType, WebhookDeliveryRecord, WebhookEventRecord,
  WebhookEndpoint, WebhookFilterState, WebhookRetrySchedule
} from '@/components/webhooks/webhook-types';

import {
  PRODUCTION_ENDPOINTS,
  PRODUCTION_EVENTS,
  PRODUCTION_DELIVERIES,
  PRODUCTION_SUBSCRIPTIONS,
  PRODUCTION_RETRIES,
  PRODUCTION_SECURITY,
  PRODUCTION_AUDIT
} from '@/components/webhooks/webhook-data';

export default function WebhookOperationsPage() {
  const [activeTab, setActiveTab] = useState<WebhookTabType>('REGISTRY');
  const [selectedDelivery, setSelectedDelivery] = useState<WebhookDeliveryRecord | null>(null);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [endpoints, setEndpoints] = useState<WebhookEndpoint[]>(PRODUCTION_ENDPOINTS);

  const [filters, setFilters] = useState<WebhookFilterState>({
    searchQuery: '',
    status: 'ALL',
    eventType: 'ALL',
    endpoint: 'ALL',
    environment: 'ALL',
    httpStatus: 'ALL',
  });

  const filteredEndpoints = useMemo(() => {
    return endpoints.filter((ep) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        ep.endpointId.toLowerCase().includes(q) ||
        ep.name.toLowerCase().includes(q) ||
        ep.url.toLowerCase().includes(q);
      const matchStatus = filters.status === 'ALL' || ep.status === filters.status;
      const matchEndpoint = filters.endpoint === 'ALL' || ep.endpointId === filters.endpoint;
      const matchEnv = filters.environment === 'ALL' || ep.environment === filters.environment;
      return matchSearch && matchStatus && matchEndpoint && matchEnv;
    });
  }, [endpoints, filters]);

  const filteredEvents = useMemo(() => {
    return PRODUCTION_EVENTS.filter((evt) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        evt.eventId.toLowerCase().includes(q) ||
        evt.eventType.toLowerCase().includes(q) ||
        evt.resourceId.toLowerCase().includes(q) ||
        evt.agentId.toLowerCase().includes(q);
      const matchType = filters.eventType === 'ALL' || evt.eventType === filters.eventType;
      const matchEnv = filters.environment === 'ALL' || evt.environment === filters.environment;
      return matchSearch && matchType && matchEnv;
    });
  }, [filters]);

  const filteredDeliveries = useMemo(() => {
    return PRODUCTION_DELIVERIES.filter((dlv) => {
      const q = filters.searchQuery.toLowerCase();
      const matchSearch = !q ||
        dlv.deliveryId.toLowerCase().includes(q) ||
        dlv.eventId.toLowerCase().includes(q) ||
        dlv.endpointId.toLowerCase().includes(q) ||
        dlv.endpointName.toLowerCase().includes(q) ||
        dlv.agentId.toLowerCase().includes(q);
      const matchStatus = filters.status === 'ALL' || dlv.status === filters.status;
      const matchType = filters.eventType === 'ALL' || dlv.eventType === filters.eventType;
      const matchEndpoint = filters.endpoint === 'ALL' || dlv.endpointId === filters.endpoint;
      const matchEnv = filters.environment === 'ALL' || dlv.environment === filters.environment;
      const matchHttp = filters.httpStatus === 'ALL' || String(dlv.responseStatus) === filters.httpStatus;
      return matchSearch && matchStatus && matchType && matchEndpoint && matchEnv && matchHttp;
    });
  }, [filters]);

  const handleSelectEndpoint = (ep: WebhookEndpoint) => {
    // Find delivery matching endpoint or first available
    const match = PRODUCTION_DELIVERIES.find(d => d.endpointId === ep.endpointId) || PRODUCTION_DELIVERIES[0];
    setSelectedDelivery(match);
  };

  const handleSelectEvent = (evt: WebhookEventRecord) => {
    const match = PRODUCTION_DELIVERIES.find(d => d.eventId === evt.eventId) || PRODUCTION_DELIVERIES[0];
    setSelectedDelivery(match);
  };

  const handleReplayDelivery = (dlv: WebhookDeliveryRecord) => {
    alert(`[SIMULATED REPLAY QUEUED] Replaying delivery ${dlv.deliveryId} for event ${dlv.eventId} to ${dlv.endpointName}.`);
  };

  const handleReplayRetry = (ret: WebhookRetrySchedule) => {
    alert(`[SIMULATED REPLAY QUEUED] Triggering immediate retry for ${ret.deliveryId} (${ret.retryId}).`);
  };

  const handleRegisterEndpoint = (data: { name: string; url: string; env: string; auth: string }) => {
    const newId = `WHK-00${endpoints.length + 1}`;
    const newEp: WebhookEndpoint = {
      id: `whk_${endpoints.length + 1}`,
      endpointId: newId,
      name: data.name,
      url: data.url,
      environment: data.env as any,
      subscribedEventsCount: 12,
      status: 'ACTIVE',
      healthScore: 100.0,
      lastDelivery: 'Just now',
      successRate: 100.0,
      p95LatencyMs: 110,
      failedCount24h: 0,
      secretMasked: 'whsec_••••••••A91F',
      secretRotationDays: 90,
      authType: data.auth as any,
      createdAt: '2026-08-30',
      updatedAt: '2026-08-30 09:30:00'
    };
    setEndpoints([newEp, ...endpoints]);
    setIsRegisterOpen(false);
    alert(`Endpoint ${newId} (${data.name}) successfully registered!`);
  };

  const handleReset = () => {
    setFilters({
      searchQuery: '', status: 'ALL', eventType: 'ALL',
      endpoint: 'ALL', environment: 'ALL', httpStatus: 'ALL',
    });
  };

  const failedCount = PRODUCTION_DELIVERIES.filter(d => d.status === 'FAILED' || d.status === 'EXHAUSTED').length;

  return (
    <AgentPayShell activeTab="webhooks">
      <div className="space-y-6 pb-12">

        {/* HEADER */}
        <WebhookHeader
          onRefresh={() => alert('Webhook telemetry feed refreshed.')}
          onExport={() => alert('Exporting webhook event ledger...')}
          onRegister={() => setIsRegisterOpen(true)}
        />

        {/* METRICS */}
        <WebhookMetrics
          endpointCount={endpoints.length}
          deliveryCount={18492}
          successRate="99.72%"
          p95Latency="184ms"
          failedCount={failedCount + PRODUCTION_RETRIES.length}
          deadLetterCount={1}
        />

        {/* CONTROLS */}
        <WebhookControls
          searchQuery={filters.searchQuery}
          onSearchChange={(v) => setFilters(f => ({ ...f, searchQuery: v }))}
          selectedStatus={filters.status}
          onStatusChange={(v) => setFilters(f => ({ ...f, status: v }))}
          selectedEventType={filters.eventType}
          onEventTypeChange={(v) => setFilters(f => ({ ...f, eventType: v }))}
          selectedEndpoint={filters.endpoint}
          onEndpointChange={(v) => setFilters(f => ({ ...f, endpoint: v }))}
          selectedEnvironment={filters.environment}
          onEnvironmentChange={(v) => setFilters(f => ({ ...f, environment: v }))}
          selectedHttpStatus={filters.httpStatus}
          onHttpStatusChange={(v) => setFilters(f => ({ ...f, httpStatus: v }))}
          onReset={handleReset}
        />

        {/* TABS */}
        <WebhookTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          registryCount={filteredEndpoints.length}
          eventCount={filteredEvents.length}
          deliveryCount={filteredDeliveries.length}
          subscriptionCount={PRODUCTION_SUBSCRIPTIONS.length}
          retryCount={PRODUCTION_RETRIES.length}
          securityCount={PRODUCTION_SECURITY.length}
          auditCount={PRODUCTION_AUDIT.length}
        />

        {/* TAB CONTENT */}
        {activeTab === 'REGISTRY' && (
          <WebhookRegistry
            endpoints={filteredEndpoints}
            onSelect={handleSelectEndpoint}
          />
        )}

        {activeTab === 'EVENTS' && (
          <WebhookEvents
            events={filteredEvents}
            onSelect={handleSelectEvent}
          />
        )}

        {activeTab === 'DELIVERIES' && (
          <WebhookDeliveries
            deliveries={filteredDeliveries}
            onSelect={setSelectedDelivery}
          />
        )}

        {activeTab === 'SUBSCRIPTIONS' && (
          <WebhookSubscriptions subscriptions={PRODUCTION_SUBSCRIPTIONS} />
        )}

        {activeTab === 'RETRIES' && (
          <WebhookRetries
            retries={PRODUCTION_RETRIES}
            onReplay={handleReplayRetry}
          />
        )}

        {activeTab === 'SECURITY' && (
          <WebhookSecurity records={PRODUCTION_SECURITY} />
        )}

        {activeTab === 'AUDIT' && (
          <WebhookAudit entries={PRODUCTION_AUDIT} />
        )}

        {/* INSPECTOR DRAWER */}
        <WebhookInspector
          delivery={selectedDelivery}
          onClose={() => setSelectedDelivery(null)}
          onReplay={handleReplayDelivery}
        />

        {/* REGISTER MODAL */}
        <RegisterWebhookModal
          isOpen={isRegisterOpen}
          onClose={() => setIsRegisterOpen(false)}
          onRegister={handleRegisterEndpoint}
        />

      </div>
    </AgentPayShell>
  );
}
