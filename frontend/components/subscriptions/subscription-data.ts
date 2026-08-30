import { SubscriptionRecord } from './subscription-types';
export const MOCK_SUBSCRIPTIONS: SubscriptionRecord[] = [
  { id: 's1', subscriptionId: 'SUB-AGP-001', planName: 'Enterprise Autonomy Tier', customer: 'CUS-AGP-001', agentId: 'AGT-892', amount: '$4,999.00', interval: 'Monthly', status: 'ACTIVE', currentPeriodEnd: '2026-09-30', paymentMethod: 'VISA •••• 4821', riskScore: 12 },
  { id: 's2', subscriptionId: 'SUB-AGP-002', planName: 'Vendor Settlement Pro', customer: 'CUS-AGP-002', agentId: 'AGT-441', amount: '$2,499.00', interval: 'Monthly', status: 'ACTIVE', currentPeriodEnd: '2026-09-15', paymentMethod: 'BANK •••• 9921', riskScore: 8 },
];
