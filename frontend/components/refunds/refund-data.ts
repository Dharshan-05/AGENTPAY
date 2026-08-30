import { RefundRecord } from './refund-types';

export const MOCK_REFUNDS: RefundRecord[] = [
  { id: 'r1', refundId: 'REF-AGP-001', transactionId: 'TXN-AGP-91F2', paymentIntentId: 'PI-AGP-001', amount: '$450.00', currency: 'USD', reason: 'Customer Cancellation', requestedBy: 'Support Admin', agentId: 'AGT-892', status: 'SUCCEEDED', processor: 'Stripe', createdAt: '1h ago' },
  { id: 'r2', refundId: 'REF-AGP-002', transactionId: 'TXN-AGP-4410', paymentIntentId: 'PI-AGP-002', amount: '$2,070.00', currency: 'USD', reason: 'Partial Order Adjustment', requestedBy: 'Automated Policy', agentId: 'AGT-441', status: 'SUCCEEDED', processor: 'JPMorgan Direct', createdAt: '4h ago' },
  { id: 'r3', refundId: 'REF-AGP-003', transactionId: 'TXN-AGP-1180', paymentIntentId: 'PI-AGP-003', amount: '₹25,000.00', currency: 'INR', reason: 'Reconciliation Return', requestedBy: 'Agent Governance', agentId: 'AGT-118', status: 'PROCESSING', processor: 'Razorpay', createdAt: '30m ago' },
];
