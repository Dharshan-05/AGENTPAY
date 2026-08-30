import { SettlementRecord } from './settlement-types';

export const MOCK_SETTLEMENTS: SettlementRecord[] = [
  { id: 's1', settlementId: 'SET-AGP-001', batchId: 'BAT-2026-0830A', merchantId: 'MER-AGP-001', processor: 'Stripe', grossAmount: '$781,680.00', fees: '$4,849.00', netAmount: '$776,831.00', currency: 'USD', settlementDate: '2026-08-30', status: 'SETTLED', ledgerRef: 'LED-AGP-9901' },
  { id: 's2', settlementId: 'SET-AGP-002', batchId: 'BAT-2026-0830B', merchantId: 'MER-AGP-002', processor: 'Adyen', grossAmount: '€512,000.00', fees: '€3,100.00', netAmount: '€508,900.00', currency: 'EUR', settlementDate: '2026-08-30', status: 'SETTLED', ledgerRef: 'LED-AGP-9902' },
  { id: 's3', settlementId: 'SET-AGP-003', batchId: 'BAT-2026-0830C', merchantId: 'MER-AGP-003', processor: 'Razorpay', grossAmount: '₹12,500,000.00', fees: '₹125,000.00', netAmount: '₹12,375,000.00', currency: 'INR', settlementDate: '2026-08-30', status: 'PROCESSING', ledgerRef: 'LED-AGP-9903' },
];
