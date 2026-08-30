import { StoreCreditRecord } from './store-credit-types';
export const MOCK_STORE_CREDIT: StoreCreditRecord[] = [
  { id: 'sc1', creditId: 'SCR-AGP-001', customer: 'CUS-AGP-001 (Acme AI)', balance: '$4,250.00', currency: 'USD', lastMovement: '+$500.00 (Refund Return)', autoApply: true, status: 'ACTIVE' },
  { id: 'sc2', creditId: 'SCR-AGP-002', customer: 'CUS-AGP-002 (Global Tech)', balance: '€1,100.00', currency: 'EUR', lastMovement: '-€200.00 (Order #882)', autoApply: true, status: 'ACTIVE' },
];
