import { RecurringPaymentRecord } from './recurring-payment-types';
export const MOCK_RECURRING: RecurringPaymentRecord[] = [
  { id: 'r1', recurringId: 'REC-AGP-001', mandateRef: 'MAN-AGP-001', agentId: 'AGT-892', amount: '$4,999.00', nextExecutionDate: '2026-09-01 00:00:00', retryAttempt: 0, status: 'SCHEDULED' },
  { id: 'r2', recurringId: 'REC-AGP-002', mandateRef: 'MAN-AGP-002', agentId: 'AGT-118', amount: '₹150,000.00', nextExecutionDate: '2026-09-05 00:00:00', retryAttempt: 0, status: 'SCHEDULED' },
];
