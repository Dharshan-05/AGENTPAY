import { SettlementReconciliationRecord } from './settlement-reconciliation-types';
export const MOCK_SETTLEMENT_RECONCILIATION: SettlementReconciliationRecord[] = [
  { id: 'sr1', batchId: 'SREC-AGP-001', processor: 'STRIPE_CONNECT', grossAmount: '$245,800.00', feesDeducted: '$4,916.00', netSettled: '$240,884.00', matchedTransactions: 1420, variance: '$0.00', status: 'RECONCILED' },
  { id: 'sr2', batchId: 'SREC-AGP-002', processor: 'ADYEN_GLOBAL', grossAmount: '€180,450.00', feesDeducted: '€3,609.00', netSettled: '€176,841.00', matchedTransactions: 890, variance: '€0.00', status: 'RECONCILED' },
];
