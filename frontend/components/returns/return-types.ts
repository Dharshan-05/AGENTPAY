'use client';
export type ReturnsTabType = 'REQUESTS' | 'APPROVED' | 'IN_INSPECTION' | 'REFUNDED' | 'REJECTED' | 'REASON_CODES' | 'AUDIT';
export interface ReturnRecord {
  id: string;
  rmaId: string;
  orderId: string;
  customer: string;
  reason: string;
  refundAmount: string;
  inspectionState: 'PASSED' | 'PENDING' | 'FAILED';
  status: 'APPROVED' | 'IN_INSPECTION' | 'COMPLETED';
}
