'use client';
export type StockReservationsTabType = 'RESERVATIONS' | 'TTL_MONITOR' | 'EXPIRATIONS' | 'RELEASED' | 'FULFILLED' | 'AUDIT';
export interface StockReservationRecord {
  id: string;
  reservationId: string;
  orderRef: string;
  sku: string;
  quantity: number;
  ttlRemainingMinutes: number;
  warehouse: string;
  status: 'ACTIVE' | 'FULFILLED' | 'RELEASED' | 'EXPIRED';
}
