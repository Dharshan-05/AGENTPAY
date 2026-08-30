import { CheckoutSessionRecord } from './checkout-types';
export const MOCK_CHECKOUT_SESSIONS: CheckoutSessionRecord[] = [
  { id: 'c1', sessionId: 'CHK-AGP-001', agentId: 'AGT-892', merchant: 'Cloud Host Inc', amount: '$781,680.00', threeDsStatus: 'AUTHENTICATED', processor: 'Stripe', status: 'COMPLETED' },
  { id: 'c2', sessionId: 'CHK-AGP-002', agentId: 'AGT-441', merchant: 'Global Logistics Corp', amount: '$12,500.00', threeDsStatus: 'PASSED', processor: 'Adyen', status: 'COMPLETED' },
];
