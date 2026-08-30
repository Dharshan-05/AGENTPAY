import { AttemptRecord } from './payment-attempt-types';
export const MOCK_ATTEMPTS: AttemptRecord[] = [
  { id: 'at1', attemptId: 'ATT-AGP-001', paymentIntentId: 'PI-AGP-9120', orderId: 'ORD-AGP-001', processor: 'Stripe', attemptNumber: 1, amount: '$12,999.00', latencyMs: 142, responseCode: '200_OK_AUTH', status: 'AUTHORIZED' },
  { id: 'at2', attemptId: 'ATT-AGP-002', paymentIntentId: 'PI-AGP-4412', orderId: 'ORD-AGP-002', processor: 'Adyen', attemptNumber: 1, amount: '€2,499.00', latencyMs: 118, responseCode: '200_OK_CAPTURED', status: 'CAPTURED' },
];
