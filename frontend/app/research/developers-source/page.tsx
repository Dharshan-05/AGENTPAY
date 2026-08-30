'use client';

import { useState } from 'react';
import './developers-source.css';
import { SourceHeader } from '@/components/research/developers/source-header';
import { SourceKeysTable } from '@/components/research/developers/source-keys-table';
import { SourceWebhooks } from '@/components/research/developers/source-webhooks';
import { SourceSdkTester } from '@/components/research/developers/source-sdk-tester';
import { SourceLogsTable } from '@/components/research/developers/source-logs-table';
import { SourceKeyModal } from '@/components/research/developers/source-key-modal';
import { SourceInspector } from '@/components/research/developers/source-inspector';
import {
  SourceApiKeyRecord,
  SourceWebhookEndpointRecord,
  SourceDeveloperLogRecord,
} from '@/components/research/developers/source-types';

const MOCK_KEYS: SourceApiKeyRecord[] = [
  {
    id: 'key_live_9981a',
    name: 'Production Procurement Agent Key',
    keyPrefix: 'ag_live_9981a7b',
    created: '2026-08-01 10:14 UTC',
    lastUsed: 'Just now',
    scope: 'FULL_ACCESS',
    environment: 'PRODUCTION',
    status: 'ACTIVE',
  },
  {
    id: 'key_live_4412b',
    name: 'Shopping Agent Micro-Transactions',
    keyPrefix: 'ag_live_4412b9c',
    created: '2026-08-12 14:20 UTC',
    lastUsed: '5 mins ago',
    scope: 'PAYMENTS_ONLY',
    environment: 'PRODUCTION',
    status: 'ACTIVE',
  },
  {
    id: 'key_test_2039c',
    name: 'Sandbox Integration Test Token',
    keyPrefix: 'ag_test_2039c1d',
    created: '2026-08-20 09:30 UTC',
    lastUsed: '1 hour ago',
    scope: 'READ_ONLY',
    environment: 'SANDBOX',
    status: 'ACTIVE',
  },
];

const MOCK_WEBHOOKS: SourceWebhookEndpointRecord[] = [
  {
    id: 'wh_1092',
    url: 'https://api.merchant.com/v1/webhooks/agentpay',
    events: ['payment.authorized', 'payment.captured', 'settlement.created'],
    status: 'ACTIVE',
    signingSecret: 'whsec_live_9981273918237498127',
    created: '2026-08-05 11:00 UTC',
  },
];

const MOCK_LOGS: SourceDeveloperLogRecord[] = [
  { id: 'log_1', method: 'POST', endpoint: '/v1/intent/authorize', statusCode: 200, latency: '124ms', ipAddress: '103.14.88.19', timestamp: '02:14:22 UTC' },
  { id: 'log_2', method: 'GET', endpoint: '/v1/agents/AGT-892/limits', statusCode: 200, latency: '14ms', ipAddress: '198.51.100.42', timestamp: '02:10:18 UTC' },
  { id: 'log_3', method: 'POST', endpoint: '/v1/payments/capture', statusCode: 200, latency: '88ms', ipAddress: '12.180.44.12', timestamp: '01:58:44 UTC' },
];

export default function DevelopersSourceResearchPage() {
  const [activeTab, setActiveTab] = useState<string>('KEYS');
  const [keys, setKeys] = useState<SourceApiKeyRecord[]>(MOCK_KEYS);
  const [webhooks] = useState<SourceWebhookEndpointRecord[]>(MOCK_WEBHOOKS);
  const [logs] = useState<SourceDeveloperLogRecord[]>(MOCK_LOGS);

  const [selectedKey, setSelectedKey] = useState<SourceApiKeyRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleCreateKey = (
    name: string,
    environment: 'PRODUCTION' | 'SANDBOX',
    scope: 'FULL_ACCESS' | 'READ_ONLY' | 'PAYMENTS_ONLY'
  ) => {
    const newKey: SourceApiKeyRecord = {
      id: `key_${environment.toLowerCase()}_${Math.random().toString(36).substring(2, 7)}`,
      name,
      keyPrefix: `ag_${environment.toLowerCase().substring(0, 4)}_${Math.random().toString(36).substring(2, 9)}`,
      created: `${new Date().toISOString().substring(0, 10)} ${new Date().toISOString().substring(11, 16)} UTC`,
      lastUsed: 'Never',
      scope,
      environment,
      status: 'ACTIVE',
    };
    setKeys((prev) => [newKey, ...prev]);
  };

  const handleRevokeKey = (id: string) => {
    setKeys((prev) =>
      prev.map((k) => (k.id === id ? { ...k, status: 'REVOKED' as const } : k))
    );
  };

  return (
    <div className="developers-source-root min-h-screen p-6 space-y-6 bg-slate-100 font-sans">
      
      {/* HEADER */}
      <SourceHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onOpenCreateKeyModal={() => setIsModalOpen(true)}
      />

      {/* TAB CONTENTS */}
      {activeTab === 'KEYS' && (
        <SourceKeysTable
          keys={keys}
          onSelectKey={(key) => setSelectedKey(key)}
          onRevokeKey={handleRevokeKey}
        />
      )}

      {activeTab === 'WEBHOOKS' && <SourceWebhooks webhooks={webhooks} />}

      {activeTab === 'SDK_TESTER' && <SourceSdkTester />}

      {activeTab === 'LOGS' && <SourceLogsTable logs={logs} />}

      {/* CREATE KEY MODAL */}
      <SourceKeyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreateKey={handleCreateKey}
      />

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        keyItem={selectedKey}
        onClose={() => setSelectedKey(null)}
      />

    </div>
  );
}
