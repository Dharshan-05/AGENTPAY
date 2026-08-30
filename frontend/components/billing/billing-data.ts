import { BillingRecord } from './billing-types';
export const MOCK_BILLING: BillingRecord[] = [
  { id: 'b1', billingId: 'BIL-AGP-001', customer: 'CUS-AGP-001', cyclePeriod: 'Aug 2026', usageUnits: 1420, meteredAmount: '$1,420.00', balance: '$0.00', status: 'CURRENT' },
  { id: 'b2', billingId: 'BIL-AGP-002', customer: 'CUS-AGP-002', cyclePeriod: 'Aug 2026', usageUnits: 890, meteredAmount: '€890.00', balance: '€0.00', status: 'CURRENT' },
];
