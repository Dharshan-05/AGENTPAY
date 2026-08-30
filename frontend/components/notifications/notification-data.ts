import { NotificationRecord } from './notification-types';
export const MOCK_NOTIFICATIONS: NotificationRecord[] = [
  { id: 'n1', notificationId: 'NTF-AGP-001', event: 'payment_intent.succeeded', channel: 'WEBHOOK', target: 'https://api.merchant.com/wh', status: 'DELIVERED', latencyMs: 48, timestamp: '2026-08-30 09:14:01' },
  { id: 'n2', notificationId: 'NTF-AGP-002', event: 'fraudguard.high_risk_flagged', channel: 'SLACK', target: '#secops-alerts', status: 'DELIVERED', latencyMs: 92, timestamp: '2026-08-30 08:30:05' },
];
