import { ReservationRecord } from './inventory-reservation-types';
export const MOCK_RESERVATIONS: ReservationRecord[] = [
  { id: 'r1', reservationId: 'RES-AGP-001', orderId: 'ORD-AGP-001', sku: 'SKU-COMPUTE-100K', quantity: 2, reservedAt: '2026-08-30 09:14:00', expiresAt: '2026-08-30 09:44:00', status: 'COMMITTED' },
  { id: 'r2', reservationId: 'RES-AGP-002', orderId: 'ORD-AGP-002', sku: 'SKU-GOV-ANNUAL', quantity: 1, reservedAt: '2026-08-30 08:30:00', expiresAt: '2026-08-30 09:00:00', status: 'ACTIVE' },
];
