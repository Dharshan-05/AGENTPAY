import { FeeRecord } from './fee-types';
export const MOCK_FEES: FeeRecord[] = [
  { id: 'f1', feeId: 'FEE-AGP-001', transactionRef: 'TXN-AGP-91F2', processor: 'Stripe', interchangeFee: '$3,820.00', schemeFee: '$512.00', platformMargin: '$517.00', totalFees: '$4,849.00', effectiveRate: '0.62%' },
  { id: 'f2', feeId: 'FEE-AGP-002', transactionRef: 'TXN-AGP-4410', processor: 'Adyen', interchangeFee: '€2,400.00', schemeFee: '€350.00', platformMargin: '€350.00', totalFees: '€3,100.00', effectiveRate: '0.60%' },
];
