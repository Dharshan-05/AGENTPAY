import { PayoutRecord } from './payout-types';

export const MOCK_PAYOUTS: PayoutRecord[] = [
  { id: 'p1', payoutId: 'PO-AGP-001', merchantId: 'MER-AGP-001', amount: '$776,831.00', currency: 'USD', destination: 'BANK •••• 9921', bankName: 'JPMorgan Chase', processor: 'JPMorgan Direct', status: 'COMPLETED', expectedArrival: '2026-08-30', riskScore: 8 },
  { id: 'p2', payoutId: 'PO-AGP-002', merchantId: 'MER-AGP-002', amount: '€508,900.00', currency: 'EUR', destination: 'IBAN •••• 8820', bankName: 'Deutsche Bank', processor: 'Adyen', status: 'PROCESSING', expectedArrival: '2026-08-31', riskScore: 12 },
];
