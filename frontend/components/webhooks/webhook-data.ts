import {
  WebhookEndpoint, WebhookEventRecord, WebhookSubscription,
  WebhookDeliveryRecord, WebhookRetrySchedule, WebhookSecurityRecord,
  WebhookAuditEvent
} from './webhook-types';

export const PRODUCTION_ENDPOINTS: WebhookEndpoint[] = [
  {
    id: 'whk_1', endpointId: 'WHK-001', name: 'Finance Operations Gateway',
    url: 'https://api.acme-corp.test/webhooks/finance', environment: 'PRODUCTION',
    subscribedEventsCount: 18, status: 'HEALTHY', healthScore: 99.92,
    lastDelivery: '2m ago', successRate: 99.92, p95LatencyMs: 142, failedCount24h: 1,
    secretMasked: 'whsec_••••••••91F2', secretRotationDays: 14, authType: 'HMAC_SHA256',
    createdAt: '2026-01-15', updatedAt: '2026-08-30 09:15:00'
  },
  {
    id: 'whk_2', endpointId: 'WHK-002', name: 'Fraud & Risk Realtime Monitor',
    url: 'https://risk-api.sentinel-sec.test/v1/agent-alerts', environment: 'PRODUCTION',
    subscribedEventsCount: 9, status: 'DEGRADED', healthScore: 97.31,
    lastDelivery: '5m ago', successRate: 97.31, p95LatencyMs: 388, failedCount24h: 14,
    secretMasked: 'whsec_••••••••88A1', secretRotationDays: 3, authType: 'MTLS',
    createdAt: '2026-02-10', updatedAt: '2026-08-30 09:10:00'
  },
  {
    id: 'whk_3', endpointId: 'WHK-003', name: 'ERP Ledger Sync (NetSuite)',
    url: 'https://integrations.netsuite-bridge.test/netsuite/webhooks', environment: 'PRODUCTION',
    subscribedEventsCount: 12, status: 'ACTIVE', healthScore: 100.0,
    lastDelivery: '12m ago', successRate: 100.0, p95LatencyMs: 195, failedCount24h: 0,
    secretMasked: 'whsec_••••••••44C7', secretRotationDays: 45, authType: 'HMAC_SHA256',
    createdAt: '2026-03-01', updatedAt: '2026-08-30 08:45:00'
  },
  {
    id: 'whk_4', endpointId: 'WHK-004', name: 'Developer Sandbox Receiver',
    url: 'https://webhook.site/test-sandbox-agentpay-9921', environment: 'SANDBOX',
    subscribedEventsCount: 24, status: 'ACTIVE', healthScore: 100.0,
    lastDelivery: '1m ago', successRate: 100.0, p95LatencyMs: 91, failedCount24h: 0,
    secretMasked: 'whsec_••••••••00X1', secretRotationDays: 90, authType: 'BEARER_TOKEN',
    createdAt: '2026-04-12', updatedAt: '2026-08-30 09:20:00'
  },
  {
    id: 'whk_5', endpointId: 'WHK-005', name: 'Legacy Accounting Collector',
    url: 'https://legacy-billing.acme.test/api/events', environment: 'PRODUCTION',
    subscribedEventsCount: 6, status: 'FAILING', healthScore: 82.4,
    lastDelivery: '18m ago', successRate: 82.4, p95LatencyMs: 1420, failedCount24h: 38,
    secretMasked: 'whsec_••••••••77Z9', secretRotationDays: 0, authType: 'BASIC_AUTH',
    createdAt: '2025-11-20', updatedAt: '2026-08-30 08:00:00'
  },
  {
    id: 'whk_6', endpointId: 'WHK-006', name: 'Staging Compliance Webhook',
    url: 'https://staging-compliance.acme.test/events', environment: 'STAGING',
    subscribedEventsCount: 15, status: 'PAUSED', healthScore: 99.1,
    lastDelivery: '2h ago', successRate: 99.1, p95LatencyMs: 110, failedCount24h: 0,
    secretMasked: 'whsec_••••••••11M2', secretRotationDays: 60, authType: 'HMAC_SHA256',
    createdAt: '2026-05-04', updatedAt: '2026-08-30 07:15:00'
  }
];

export const PRODUCTION_EVENTS: WebhookEventRecord[] = [
  {
    id: 'evt_1', eventId: 'EVT-AGP-98271', eventType: 'transaction.captured',
    resourceType: 'TRANSACTION', resourceId: 'TXN-AGP-91F2', agentId: 'AGT-892',
    agentName: 'Procurement Agent', transactionId: 'TXN-AGP-91F2', policyId: 'AGP-GOV-001',
    severity: 'INFO', environment: 'PRODUCTION', deliveryCount: 3, createdTimestamp: '2026-08-30 09:14:01',
    payloadJson: JSON.stringify({
      event_id: 'EVT-AGP-98271', event_type: 'transaction.captured', timestamp: '2026-08-30T09:14:01Z',
      data: { transaction_id: 'TXN-AGP-91F2', intent_id: 'PI-AGP-98271', agent_id: 'AGT-892', amount: 4820.00, currency: 'USD', merchant: 'Acme Industrial Supplies', processor: 'Stripe', authorization_code: 'AUTH-9921X', settlement_batch: 'STL-881' }
    }, null, 2)
  },
  {
    id: 'evt_2', eventId: 'EVT-AGP-98272', eventType: 'policy.blocked',
    resourceType: 'POLICY', resourceId: 'AGP-GOV-001', agentId: 'AGT-892',
    agentName: 'Procurement Agent', transactionId: 'TXN-AGP-11A8', policyId: 'AGP-GOV-001',
    severity: 'CRITICAL', environment: 'PRODUCTION', deliveryCount: 2, createdTimestamp: '2026-08-30 08:41:19',
    payloadJson: JSON.stringify({
      event_id: 'EVT-AGP-98272', event_type: 'policy.blocked', timestamp: '2026-08-30T08:41:19Z',
      data: { transaction_id: 'TXN-AGP-11A8', policy_id: 'AGP-GOV-001', agent_id: 'AGT-892', amount: 48200.00, limit: 10000.00, reason: 'SPEND_LIMIT_EXCEEDED', hitl_required: true }
    }, null, 2)
  },
  {
    id: 'evt_3', eventId: 'EVT-AGP-98273', eventType: 'risk.alerted',
    resourceType: 'RISK', resourceId: 'RSK-9901A', agentId: 'AGT-441',
    agentName: 'Vendor Payment Agent', transactionId: 'TXN-AGP-82A1', policyId: 'AGP-GOV-002',
    severity: 'WARNING', environment: 'PRODUCTION', deliveryCount: 1, createdTimestamp: '2026-08-29 11:08:29',
    payloadJson: JSON.stringify({
      event_id: 'EVT-AGP-98273', event_type: 'risk.alerted', timestamp: '2026-08-29T11:08:29Z',
      data: { transaction_id: 'TXN-AGP-82A1', risk_score: 62, risk_tier: 'HIGH', velocity_flag: true, geo_risk: 'LOW', recommendation: 'HITL_REVIEW' }
    }, null, 2)
  },
  {
    id: 'evt_4', eventId: 'EVT-AGP-98274', eventType: 'refund.succeeded',
    resourceType: 'REFUND', resourceId: 'REF-AGP-7712', agentId: 'AGT-118',
    agentName: 'Invoice Reconciliation Agent', transactionId: 'TXN-AGP-44F7',
    severity: 'INFO', environment: 'PRODUCTION', deliveryCount: 2, createdTimestamp: '2026-08-29 15:12:40',
    payloadJson: JSON.stringify({
      event_id: 'EVT-AGP-98274', event_type: 'refund.succeeded', timestamp: '2026-08-29T15:12:40Z',
      data: { refund_id: 'REF-AGP-7712', transaction_id: 'TXN-AGP-44F7', amount: 3680.00, currency: 'USD', reason: 'DUPLICATE_CHARGE' }
    }, null, 2)
  },
  {
    id: 'evt_5', eventId: 'EVT-AGP-98275', eventType: 'agent.suspended',
    resourceType: 'AGENT', resourceId: 'AGT-990', agentId: 'AGT-990',
    agentName: 'Experimental Trading Agent', severity: 'CRITICAL', environment: 'STAGING',
    deliveryCount: 1, createdTimestamp: '2026-08-30 07:15:00',
    payloadJson: JSON.stringify({
      event_id: 'EVT-AGP-98275', event_type: 'agent.suspended', timestamp: '2026-08-30T07:15:00Z',
      data: { agent_id: 'AGT-990', status: 'SUSPENDED', reason: 'POLICY_VARIANCE_BREACH', suspended_by: 'AGP-GOV-AUTO' }
    }, null, 2)
  }
];

export const PRODUCTION_DELIVERIES: WebhookDeliveryRecord[] = [
  {
    id: 'dlv_1', deliveryId: 'DLV-AGP-88191', eventId: 'EVT-AGP-98271',
    eventType: 'transaction.captured', endpointId: 'WHK-001',
    endpointName: 'Finance Operations Gateway', targetUrl: 'https://api.acme-corp.test/webhooks/finance',
    environment: 'PRODUCTION', createdTimestamp: '2026-08-30 09:14:01.050',
    completedTimestamp: '2026-08-30 09:14:01.192', status: 'DELIVERED', responseStatus: 200,
    latencyMs: 142, attemptCount: 1, maxRetries: 5, signature: 't=1788081241,v1=sha256:7f8a9b2c3d4e...',
    requestHeaders: 'Content-Type: application/json\nAgentPay-Signature: t=1788081241,v1=sha256:7f8a...\nAgentPay-Event: transaction.captured\nUser-Agent: AGENTPAY-Webhook/2.1',
    payloadJson: PRODUCTION_EVENTS[0].payloadJson,
    responseBodySnippet: '{"status":"received","processed_at":"2026-08-30T09:14:01.190Z","batch_id":"BATCH-9901"}',
    attempts: [
      { attemptNumber: 1, timestamp: '2026-08-30 09:14:01.050', responseStatus: 200, latencyMs: 142, responseHeaders: 'HTTP/1.1 200 OK\nContent-Type: application/json', responseBodySnippet: '{"status":"received"}' }
    ],
    agentId: 'AGT-892', transactionId: 'TXN-AGP-91F2'
  },
  {
    id: 'dlv_2', deliveryId: 'DLV-AGP-88192', eventId: 'EVT-AGP-98272',
    eventType: 'policy.blocked', endpointId: 'WHK-002',
    endpointName: 'Fraud & Risk Realtime Monitor', targetUrl: 'https://risk-api.sentinel-sec.test/v1/agent-alerts',
    environment: 'PRODUCTION', createdTimestamp: '2026-08-30 08:41:19.100',
    completedTimestamp: '2026-08-30 08:41:19.488', status: 'DELIVERED', responseStatus: 200,
    latencyMs: 388, attemptCount: 1, maxRetries: 5, signature: 't=1788079279,v1=sha256:1a2b3c4d...',
    requestHeaders: 'Content-Type: application/json\nAgentPay-Signature: t=1788079279,v1=sha256:...\nAgentPay-Event: policy.blocked',
    payloadJson: PRODUCTION_EVENTS[1].payloadJson,
    responseBodySnippet: '{"ack":true,"alert_queued":true,"risk_ticket":"TKT-9912"}',
    attempts: [
      { attemptNumber: 1, timestamp: '2026-08-30 08:41:19.100', responseStatus: 200, latencyMs: 388 }
    ],
    agentId: 'AGT-892', transactionId: 'TXN-AGP-11A8'
  },
  {
    id: 'dlv_3', deliveryId: 'DLV-AGP-88193', eventId: 'EVT-AGP-98272',
    eventType: 'policy.blocked', endpointId: 'WHK-005',
    endpointName: 'Legacy Accounting Collector', targetUrl: 'https://legacy-billing.acme.test/api/events',
    environment: 'PRODUCTION', createdTimestamp: '2026-08-30 08:41:19.105',
    status: 'EXHAUSTED', responseStatus: 504, latencyMs: 3000, attemptCount: 5, maxRetries: 5,
    signature: 't=1788079279,v1=sha256:99x88y77...',
    requestHeaders: 'Content-Type: application/json\nAgentPay-Signature: t=1788079279...',
    payloadJson: PRODUCTION_EVENTS[1].payloadJson,
    responseBodySnippet: '<html><body>504 Gateway Time-out</body></html>',
    attempts: [
      { attemptNumber: 1, timestamp: '2026-08-30 08:41:19.105', responseStatus: 504, latencyMs: 3000, errorMessage: 'Gateway Timeout (3000ms limit reached)' },
      { attemptNumber: 2, timestamp: '2026-08-30 08:42:19.105', responseStatus: 504, latencyMs: 3000, errorMessage: 'Gateway Timeout' },
      { attemptNumber: 3, timestamp: '2026-08-30 08:44:19.105', responseStatus: 504, latencyMs: 3000, errorMessage: 'Gateway Timeout' },
      { attemptNumber: 4, timestamp: '2026-08-30 08:48:19.105', responseStatus: 504, latencyMs: 3000, errorMessage: 'Gateway Timeout' },
      { attemptNumber: 5, timestamp: '2026-08-30 08:56:19.105', responseStatus: 504, latencyMs: 3000, errorMessage: 'Gateway Timeout - Retries Exhausted' }
    ],
    agentId: 'AGT-892', transactionId: 'TXN-AGP-11A8'
  },
  {
    id: 'dlv_4', deliveryId: 'DLV-AGP-88194', eventId: 'EVT-AGP-98273',
    eventType: 'risk.alerted', endpointId: 'WHK-002',
    endpointName: 'Fraud & Risk Realtime Monitor', targetUrl: 'https://risk-api.sentinel-sec.test/v1/agent-alerts',
    environment: 'PRODUCTION', createdTimestamp: '2026-08-29 11:08:29.200',
    completedTimestamp: '2026-08-29 11:08:29.580', status: 'DELIVERED', responseStatus: 200,
    latencyMs: 380, attemptCount: 1, maxRetries: 5, signature: 't=1788001709,v1=sha256:55aa66bb...',
    requestHeaders: 'Content-Type: application/json\nAgentPay-Signature: t=1788001709...',
    payloadJson: PRODUCTION_EVENTS[2].payloadJson,
    responseBodySnippet: '{"ticket_id":"RSK-ALERT-9921"}',
    attempts: [
      { attemptNumber: 1, timestamp: '2026-08-29 11:08:29.200', responseStatus: 200, latencyMs: 380 }
    ],
    agentId: 'AGT-441', transactionId: 'TXN-AGP-82A1'
  },
  {
    id: 'dlv_5', deliveryId: 'DLV-AGP-88195', eventId: 'EVT-AGP-98274',
    eventType: 'refund.succeeded', endpointId: 'WHK-003',
    endpointName: 'ERP Ledger Sync (NetSuite)', targetUrl: 'https://integrations.netsuite-bridge.test/netsuite/webhooks',
    environment: 'PRODUCTION', createdTimestamp: '2026-08-29 15:12:40.100',
    completedTimestamp: '2026-08-29 15:12:40.295', status: 'DELIVERED', responseStatus: 200,
    latencyMs: 195, attemptCount: 1, maxRetries: 5, signature: 't=1788016360,v1=sha256:9900aabb...',
    requestHeaders: 'Content-Type: application/json',
    payloadJson: PRODUCTION_EVENTS[3].payloadJson,
    responseBodySnippet: '{"netsuite_journal_ref":"JE-2026-0891"}',
    attempts: [
      { attemptNumber: 1, timestamp: '2026-08-29 15:12:40.100', responseStatus: 200, latencyMs: 195 }
    ],
    agentId: 'AGT-118', transactionId: 'TXN-AGP-44F7'
  }
];

export const PRODUCTION_SUBSCRIPTIONS: WebhookSubscription[] = [
  { id: 'sub_1', subscriptionId: 'SUB-001', endpointId: 'WHK-001', endpointName: 'Finance Operations Gateway', eventPattern: 'transaction.*', environment: 'PRODUCTION', filterRule: 'amount >= $1,000.00', status: 'ACTIVE', createdTimestamp: '2026-01-15', lastTriggered: '2m ago' },
  { id: 'sub_2', subscriptionId: 'SUB-002', endpointId: 'WHK-001', endpointName: 'Finance Operations Gateway', eventPattern: 'refund.*', environment: 'PRODUCTION', filterRule: 'ALL_REFUNDS', status: 'ACTIVE', createdTimestamp: '2026-01-15', lastTriggered: '1d ago' },
  { id: 'sub_3', subscriptionId: 'SUB-003', endpointId: 'WHK-002', endpointName: 'Fraud & Risk Realtime Monitor', eventPattern: 'policy.blocked', environment: 'PRODUCTION', filterRule: 'ALL_BLOCKED', status: 'ACTIVE', createdTimestamp: '2026-02-10', lastTriggered: '5m ago' },
  { id: 'sub_4', subscriptionId: 'SUB-004', endpointId: 'WHK-002', endpointName: 'Fraud & Risk Realtime Monitor', eventPattern: 'risk.alerted', environment: 'PRODUCTION', filterRule: 'risk_score >= 50', status: 'ACTIVE', createdTimestamp: '2026-02-10', lastTriggered: '1d ago' },
  { id: 'sub_5', subscriptionId: 'SUB-005', endpointId: 'WHK-003', endpointName: 'ERP Ledger Sync (NetSuite)', eventPattern: 'reconciliation.*', environment: 'PRODUCTION', filterRule: 'ALL_MATCHED', status: 'ACTIVE', createdTimestamp: '2026-03-01', lastTriggered: '12m ago' },
  { id: 'sub_6', subscriptionId: 'SUB-006', endpointId: 'WHK-004', endpointName: 'Developer Sandbox Receiver', eventPattern: '*', environment: 'SANDBOX', filterRule: 'ALL_EVENTS', status: 'ACTIVE', createdTimestamp: '2026-04-12', lastTriggered: '1m ago' },
  { id: 'sub_7', subscriptionId: 'SUB-007', endpointId: 'WHK-005', endpointName: 'Legacy Accounting Collector', eventPattern: 'transaction.captured', environment: 'PRODUCTION', filterRule: 'legacy_compat=true', status: 'PAUSED', createdTimestamp: '2025-11-20', lastTriggered: '18m ago' }
];

export const PRODUCTION_RETRIES: WebhookRetrySchedule[] = [
  { id: 'ret_1', retryId: 'RET-001', deliveryId: 'DLV-AGP-88193', eventId: 'EVT-AGP-98272', eventType: 'policy.blocked', endpointName: 'Legacy Accounting Collector', targetUrl: 'https://legacy-billing.acme.test/api/events', attemptCount: 5, maxAttempts: 5, scheduledAt: 'Exhausted', lastError: '504 Gateway Timeout', status: 'EXHAUSTED' },
  { id: 'ret_2', retryId: 'RET-002', deliveryId: 'DLV-AGP-88199', eventId: 'EVT-AGP-98275', eventType: 'agent.suspended', endpointName: 'Fraud & Risk Realtime Monitor', targetUrl: 'https://risk-api.sentinel-sec.test/v1/agent-alerts', attemptCount: 2, maxAttempts: 5, scheduledAt: 'In 2 mins (Exponential Backoff)', lastError: '503 Service Unavailable', status: 'QUEUED' }
];

export const PRODUCTION_SECURITY: WebhookSecurityRecord[] = [
  { id: 'sec_1', endpointId: 'WHK-001', endpointName: 'Finance Operations Gateway', secretMasked: 'whsec_••••••••91F2', signatureAlgorithm: 'HMAC-SHA256', mTLSStatus: 'ENFORCED', timestampToleranceSeconds: 300, ipAllowlist: ['192.0.2.14', '198.51.100.22'], secretRotatedAt: '2026-08-16', secretRotationDueDays: 14 },
  { id: 'sec_2', endpointId: 'WHK-002', endpointName: 'Fraud & Risk Realtime Monitor', secretMasked: 'whsec_••••••••88A1', signatureAlgorithm: 'HMAC-SHA256 + mTLS', mTLSStatus: 'ENFORCED', timestampToleranceSeconds: 120, ipAllowlist: ['203.0.113.88'], secretRotatedAt: '2026-06-01', secretRotationDueDays: 3 },
  { id: 'sec_3', endpointId: 'WHK-003', endpointName: 'ERP Ledger Sync (NetSuite)', secretMasked: 'whsec_••••••••44C7', signatureAlgorithm: 'HMAC-SHA256', mTLSStatus: 'OPTIONAL', timestampToleranceSeconds: 600, ipAllowlist: ['198.51.100.100'], secretRotatedAt: '2026-07-15', secretRotationDueDays: 45 }
];

export const PRODUCTION_AUDIT: WebhookAuditEvent[] = [
  { id: 'aud_1', eventId: 'AUD-WHK-001', timestamp: '2026-08-30 09:14:01', actor: 'SYSTEM', actorType: 'AUTOMATION', action: 'WEBHOOK_DELIVERY_COMPLETED', targetRef: 'DLV-AGP-88191', details: 'Delivered event EVT-AGP-98271 to WHK-001 in 142ms (HTTP 200)', ipAddress: '10.0.4.12', auditHash: 'sha256:7f8a9b2c...' },
  { id: 'aud_2', eventId: 'AUD-WHK-002', timestamp: '2026-08-30 08:56:19', actor: 'SYSTEM', actorType: 'AUTOMATION', action: 'WEBHOOK_RETRY_EXHAUSTED', targetRef: 'DLV-AGP-88193', details: 'Delivery DLV-AGP-88193 to WHK-005 exhausted 5 attempts. Moved to Dead-Letter.', ipAddress: '10.0.4.12', auditHash: 'sha256:1a2b3c4d...' },
  { id: 'aud_3', eventId: 'AUD-WHK-003', timestamp: '2026-08-30 08:00:00', actor: 'dev@acme-corp.test', actorType: 'DEVELOPER', action: 'SECRET_ROTATION_SCHEDULED', targetRef: 'WHK-002', details: 'Secret rotation scheduled for WHK-002. Dual-signing active for 24h.', ipAddress: '198.51.100.4', auditHash: 'sha256:9900aabb...' },
  { id: 'aud_4', eventId: 'AUD-WHK-004', timestamp: '2026-08-29 15:10:00', actor: 'dev@acme-corp.test', actorType: 'DEVELOPER', action: 'MANUAL_REPLAY_TRIGGERED', targetRef: 'EVT-AGP-98274', details: 'Manual replay triggered for EVT-AGP-98274 to endpoint WHK-003.', ipAddress: '198.51.100.4', auditHash: 'sha256:55aa66bb...' }
];
