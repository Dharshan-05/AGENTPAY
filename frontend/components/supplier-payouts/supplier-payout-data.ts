import { SupplierPayoutRecord } from './supplier-payout-types';
export const MOCK_SUPPLIER_PAYOUTS: SupplierPayoutRecord[] = [
  { id: 's1', payoutId: 'SUP-AGP-001', vendorName: 'CloudCompute Inc.', amount: '$85,420.00', currency: 'USD', splitPercentage: '85.0%', status: 'SETTLED' },
  { id: 's2', payoutId: 'SUP-AGP-002', vendorName: 'Neural Models EU', amount: '€42,100.00', currency: 'EUR', splitPercentage: '80.0%', status: 'SETTLED' },
];
