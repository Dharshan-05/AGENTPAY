'use client';
export type ReservationsTabType = 'ACTIVE' | 'EXPIRING' | 'COMMITTED' | 'RELEASED' | 'EXPIRED' | 'TIMELINE' | 'AUDIT';
export interface ReservationRecord {
  id: string;
  reservationId: string;
  orderId: string;
  sku: string;
  quantity: number;
  reservedAt: string;
  expiresAt: string;
  status: 'ACTIVE' | 'COMMITTED' | 'RELEASED' | 'EXPIRED';
}
