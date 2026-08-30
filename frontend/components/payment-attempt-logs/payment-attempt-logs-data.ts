import { PaymentAttemptLogsRecord } from './payment-attempt-logs-types';
export const MOCK_PAYMENT_ATTEMPT_LOGS: PaymentAttemptLogsRecord[] = [
  { id: 'pa1', attemptId: 'PALOG-AGP-001', paymentIntentRef: 'PI-AGP-001', processor: 'STRIPE_CONNECT', attemptNumber: 1, amount: '$15,399.00', responseCode: '200_AUTH_SUCCESS', latencyMs: 184, status: 'CAPTURED' },
  { id: 'pa2', attemptId: 'PALOG-AGP-002', paymentIntentRef: 'PI-AGP-002', processor: 'ADYEN_GLOBAL', attemptNumber: 1, amount: '€3,200.00', responseCode: '200_AUTH_SUCCESS', latencyMs: 210, status: 'CAPTURED' },
];
