import { WebhooksDeliveryRecord } from './webhooks-delivery-types';
export const MOCK_WEBHOOKS_DELIVERY: WebhooksDeliveryRecord[] = [
  { id: 'wh1', webhookId: 'WHK-AGP-001', eventType: 'payment_intent.succeeded', targetEndpoint: 'https://api.acme.com/agentpay/webhook', httpStatus: 200, attemptCount: 1, latencyMs: 142, status: 'DELIVERED' },
  { id: 'wh2', webhookId: 'WHK-AGP-002', eventType: 'fraudguard.decision_flagged', targetEndpoint: 'https://api.acme.com/agentpay/fraud-alerts', httpStatus: 200, attemptCount: 1, latencyMs: 89, status: 'DELIVERED' },
];
