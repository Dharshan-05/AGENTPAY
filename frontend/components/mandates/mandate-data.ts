import { MandateRecord } from './mandate-types';
export const MOCK_MANDATES: MandateRecord[] = [
  { id: 'm1', mandateId: 'MAN-AGP-001', customer: 'CUS-AGP-001', mandateType: 'ACH_DIRECT_DEBIT', maxAmount: '$50,000.00', frequency: 'As Presented', bankRef: 'JPMorgan Chase •••• 9921', status: 'ACTIVE' },
  { id: 'm2', mandateId: 'MAN-AGP-002', customer: 'CUS-AGP-003', mandateType: 'UPI_EMANDATE', maxAmount: '₹100,000.00', frequency: 'Monthly', bankRef: 'HDFC Bank •••• 8820', status: 'ACTIVE' },
];
