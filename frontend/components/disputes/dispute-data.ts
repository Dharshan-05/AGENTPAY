import { DisputeRecord } from './dispute-types';

export const MOCK_DISPUTES: DisputeRecord[] = [
  { id: 'd1', disputeId: 'DSP-AGP-001', transactionId: 'TXN-AGP-9901', customer: 'CUS-AGP-004', merchant: 'MER-AGP-001', amount: '$1,500.00', currency: 'USD', reason: 'Unrecognized Transaction', network: 'Mastercard', deadline: '2026-09-10', riskScore: 78, status: 'NEEDS_RESPONSE' },
  { id: 'd2', disputeId: 'DSP-AGP-002', transactionId: 'TXN-AGP-3010', customer: 'CUS-AGP-005', merchant: 'MER-AGP-002', amount: '€890.00', currency: 'EUR', reason: 'Product Not Delivered', network: 'Visa', deadline: '2026-09-05', riskScore: 42, status: 'UNDER_REVIEW' },
];
