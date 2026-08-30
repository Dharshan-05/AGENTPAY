import { StockReservationRecord } from './stock-reservation-types';
export const MOCK_STOCK_RESERVATIONS: StockReservationRecord[] = [
  { id: 'sr1', reservationId: 'SRES-AGP-001', orderRef: 'OMGT-AGP-001', sku: 'SKU-INF-10M-V1', quantity: 5, ttlRemainingMinutes: 14, warehouse: 'WH-US-EAST-1', status: 'ACTIVE' },
  { id: 'sr2', reservationId: 'SRES-AGP-002', orderRef: 'OMGT-AGP-002', sku: 'SKU-SEC-ENT-ANNUAL', quantity: 1, ttlRemainingMinutes: 0, warehouse: 'WH-EU-WEST-1', status: 'FULFILLED' },
];
