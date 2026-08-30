'use client';

import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { DevelopersHeader } from '@/components/developers/developers-header';
import { DeveloperMetrics } from '@/components/developers/developer-metrics';
import { DeveloperTabs, DeveloperTabType } from '@/components/developers/developer-tabs';
import { ApiKeysTable } from '@/components/developers/api-keys-table';
import { ApiKeyModal } from '@/components/developers/api-key-modal';
import { ApiKeyInspector } from '@/components/developers/api-key-inspector';
import { WebhookEvents } from '@/components/developers/webhook-events';
import { WebhookInspector } from '@/components/developers/webhook-inspector';
import { SdkTester } from '@/components/developers/sdk-tester';
import { RequestLogs } from '@/components/developers/request-logs';
import { RequestInspector } from '@/components/developers/request-inspector';
import { DeveloperSecurityPosture } from '@/components/developers/developer-security-posture';

import {
  DeveloperApiKey,
  WebhookEndpoint,
  WebhookEventRecord,
  DeveloperRequestLog,
} from '@/components/developers/developers-types';

const INITIAL_KEYS: DeveloperApiKey[] = [
  {
    id: 'key_7A91F2',
    name: 'Production Agent Gateway',
    keyPrefix: 'sk_live_agp_••••7F92',
    environment: 'PRODUCTION',
    scopes: ['payments:write', 'agents:read', 'agentguard:evaluate'],
    status: 'ACTIVE',
    created: '2026-08-01',
    lastUsed: '2 mins ago',
    requestRate: '842/min',
    agentId: 'AGT-892',
    policyId: 'AGP-GOV-001',
    riskBand: 'LOW',
    fraudGuardStatus: 'CLEAN',
    ipRestriction: true,
    rotationPeriod: '30 DAYS',
  },
  {
    id: 'key_4412B9',
    name: 'Procurement Integration',
    keyPrefix: 'sk_live_agp_••••19A4',
    environment: 'PRODUCTION',
    scopes: ['payments:write', 'payments:read'],
    status: 'ACTIVE',
    created: '2026-07-21',
    lastUsed: '8 mins ago',
    requestRate: '421/min',
    agentId: 'AGT-441',
    policyId: 'AGP-TXN-002',
    riskBand: 'LOW',
    fraudGuardStatus: 'LOW',
    ipRestriction: true,
    rotationPeriod: '30 DAYS',
  },
  {
    id: 'key_2039C1',
    name: 'Sandbox Testing Key',
    keyPrefix: 'sk_test_agp_••••A812',
    environment: 'SANDBOX',
    scopes: ['payments:*', 'agentguard:*', 'fraudguard:read'],
    status: 'SANDBOX',
    created: '2026-08-14',
    lastUsed: '12 sec ago',
    requestRate: '124/min',
    agentId: 'AGT-118',
    policyId: 'AGP-SUB-009',
    riskBand: 'LOW',
    fraudGuardStatus: 'CLEAN',
    ipRestriction: false,
    rotationPeriod: '90 DAYS',
  },
  {
    id: 'key_9981A4',
    name: 'Legacy Integration Token',
    keyPrefix: 'sk_live_agp_••••C441',
    environment: 'PRODUCTION',
    scopes: ['payments:read'],
    status: 'REVOKED',
    created: '2026-05-02',
    lastUsed: '2026-06-18',
    requestRate: '0/min',
    agentId: 'AGT-203',
    policyId: 'AGP-MER-003',
    riskBand: 'HIGH',
    fraudGuardStatus: 'MEDIUM',
    ipRestriction: true,
    rotationPeriod: '30 DAYS',
  },
];

const INITIAL_WEBHOOKS: WebhookEndpoint[] = [
  {
    id: 'wh_99182',
    url: 'https://api.demo-agent.local/webhooks/payments',
    events: ['PAYMENT.AUTHORIZED', 'PAYMENT.CAPTURED'],
    status: 'ACTIVE',
    deliveryRate: '99.98%',
    latency: '118ms',
    lastEvent: 'PAYMENT.AUTHORIZED',
    signingSecret: 'whsec_live_9981273918237498127',
    created: '2026-08-05 11:00 UTC',
  },
  {
    id: 'wh_44129',
    url: 'https://api.demo-agent.local/webhooks/risk',
    events: ['RISK.EVALUATED', 'ANOMALY.DETECTED'],
    status: 'ACTIVE',
    deliveryRate: '99.92%',
    latency: '141ms',
    lastEvent: 'RISK.EVALUATED',
    signingSecret: 'whsec_live_44129812739123A8123',
    created: '2026-08-12 14:00 UTC',
  },
];

const INITIAL_EVENTS: WebhookEventRecord[] = [
  {
    id: 'evt_8F21A',
    event: 'PAYMENT.AUTHORIZED',
    endpointUrl: 'https://api.demo-agent.local/webhooks/payments',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '128ms',
    attempts: 1,
    timestamp: '2026-08-30 08:14:22 UTC',
    signature: 'sha256=7F9100281F7A9B8411029837129A8812739182374981273',
    payload: { payment_id: 'pay_9981A7b', amount: 2480.0, status: 'AUTHORIZED', agent_id: 'AGT-892' },
  },
  {
    id: 'evt_71A92',
    event: 'RISK.EVALUATED',
    endpointUrl: 'https://api.demo-agent.local/webhooks/risk',
    status: 'DELIVERED',
    statusCode: 200,
    latency: '96ms',
    attempts: 1,
    timestamp: '2026-08-30 08:10:18 UTC',
    signature: 'sha256=4412B92019A8271C8819230018FA109981A7B2039488A0',
    payload: { agent_id: 'AGT-441', risk_score: 0.08, status: 'CLEAN' },
  },
];

const INITIAL_LOGS: DeveloperRequestLog[] = [
  {
    id: 'log_9A821F',
    requestId: 'req_9A821F',
    method: 'POST',
    endpoint: '/v1/payments/authorize',
    statusCode: 200,
    latency: '84ms',
    agentId: 'AGT-892',
    riskScore: 0.08,
    agentGuardStatus: 'PASSED',
    fraudGuardStatus: 'CLEAN',
    policyId: 'AGP-GOV-001',
    txnHash: '0x9F4AC8102E3B881900281F7A9B8411',
    timestamp: '08:14:22 UTC',
  },
  {
    id: 'log_72AF21',
    requestId: 'req_72AF21',
    method: 'POST',
    endpoint: '/v1/payments/authorize',
    statusCode: 403,
    latency: '142ms',
    agentId: 'AGT-441',
    riskScore: 0.91,
    agentGuardStatus: 'VIOLATION',
    fraudGuardStatus: 'HIGH RISK',
    policyId: 'AGP-MER-003',
    txnHash: '0x2A91D0018274A991028371982A8812',
    timestamp: '08:13:51 UTC',
  },
  {
    id: 'log_19BC21',
    requestId: 'req_19BC21',
    method: 'POST',
    endpoint: '/v1/agentguard/evaluate',
    statusCode: 200,
    latency: '76ms',
    agentId: 'AGT-118',
    riskScore: 0.12,
    agentGuardStatus: 'PASSED',
    fraudGuardStatus: 'CLEAN',
    policyId: 'AGP-GOV-001',
    txnHash: '0x7B12E8890281C99018274A99120098',
    timestamp: '08:13:22 UTC',
  },
];

export default function ProductionDevelopersPage() {
  const [activeTab, setActiveTab] = useState<DeveloperTabType>('KEYS');
  const [keys, setKeys] = useState<DeveloperApiKey[]>(INITIAL_KEYS);
  const [webhooks] = useState<WebhookEndpoint[]>(INITIAL_WEBHOOKS);
  const [events] = useState<WebhookEventRecord[]>(INITIAL_EVENTS);
  const [logs] = useState<DeveloperRequestLog[]>(INITIAL_LOGS);

  // Inspector & Modal State
  const [selectedKeyId, setSelectedKeyId] = useState<string | null>(null);
  const [selectedWebhookEvent, setSelectedWebhookEvent] = useState<WebhookEventRecord | null>(null);
  const [selectedRequestLog, setSelectedRequestLog] = useState<DeveloperRequestLog | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);

  const selectedKey = useMemo(
    () => keys.find((k) => k.id === selectedKeyId) || null,
    [keys, selectedKeyId]
  );

  const handleRevokeKey = (id: string) => {
    setKeys((prev) =>
      prev.map((k) => (k.id === id ? { ...k, status: 'REVOKED' as const, requestRate: '0/min' } : k))
    );
  };

  const handleCreateKey = (name: string, env: 'PRODUCTION' | 'SANDBOX', scopeStr: string) => {
    const newKey: DeveloperApiKey = {
      id: `key_${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
      name,
      keyPrefix: `sk_${env.toLowerCase()}_agp_••••${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
      environment: env,
      scopes: scopeStr.split(', '),
      status: env === 'SANDBOX' ? 'SANDBOX' : 'ACTIVE',
      created: new Date().toISOString().substring(0, 10),
      lastUsed: 'Just now',
      requestRate: '12/min',
      agentId: 'AGT-NEW',
      policyId: 'AGP-GOV-001',
      riskBand: 'LOW',
      fraudGuardStatus: 'CLEAN',
      ipRestriction: true,
      rotationPeriod: '30 DAYS',
    };
    setKeys((prev) => [newKey, ...prev]);
    setSelectedKeyId(newKey.id);
  };

  return (
    <AgentPayShell activeTab="developers">
      <div className="space-y-6 pb-12">
        
        {/* HEADER */}
        <DevelopersHeader
          onRefresh={() => {}}
          onExport={() => {}}
          onCreateKey={() => setIsCreateModalOpen(true)}
        />

        {/* METRICS */}
        <DeveloperMetrics
          activeKeys={24}
          newKeysThisMonth={3}
          requests24h="184,291"
          requestsTrend="+12.8%"
          webhookDelivery="99.94%"
          webhookEvents={1842}
          activeAgents={128}
        />

        {/* TABS */}
        <DeveloperTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* TAB 1: API KEYS & SECRETS */}
        {activeTab === 'KEYS' && (
          <div className="space-y-6">
            <ApiKeysTable
              keys={keys}
              selectedKeyId={selectedKeyId}
              onSelectKey={(id) => setSelectedKeyId(id)}
              onRevokeKey={handleRevokeKey}
            />

            <DeveloperSecurityPosture />
          </div>
        )}

        {/* TAB 2: WEBHOOKS & EVENTS */}
        {activeTab === 'WEBHOOKS' && (
          <WebhookEvents
            webhooks={webhooks}
            events={events}
            onSelectEvent={(evt) => setSelectedWebhookEvent(evt)}
          />
        )}

        {/* TAB 3: SDK TESTER */}
        {activeTab === 'SDK_TESTER' && <SdkTester />}

        {/* TAB 4: REQUEST LOGS */}
        {activeTab === 'LOGS' && (
          <RequestLogs
            logs={logs}
            onSelectLog={(log) => setSelectedRequestLog(log)}
          />
        )}

        {/* TAB 5: SECURITY POSTURE */}
        {activeTab === 'SECURITY' && <DeveloperSecurityPosture />}

        {/* API KEY MODAL */}
        <ApiKeyModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onCreateKey={handleCreateKey}
        />

        {/* API KEY INSPECTOR */}
        <ApiKeyInspector
          apiKey={selectedKey}
          onClose={() => setSelectedKeyId(null)}
          onRevoke={handleRevokeKey}
        />

        {/* WEBHOOK INSPECTOR */}
        <WebhookInspector
          event={selectedWebhookEvent}
          onClose={() => setSelectedWebhookEvent(null)}
        />

        {/* REQUEST INSPECTOR */}
        <RequestInspector
          log={selectedRequestLog}
          onClose={() => setSelectedRequestLog(null)}
        />

      </div>
    </AgentPayShell>
  );
}
