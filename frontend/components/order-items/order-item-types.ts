'use client';
export type OrderItemsTabType = 'REGISTRY' | 'SKUS' | 'RESERVATIONS' | 'DISCOUNTS' | 'TAX_LINES' | 'REFUND_LINKAGE' | 'AUDIT';
export interface OrderItemRecord {
  id: string;
  orderItemId: string;
  orderId: string;
  productName: string;
  sku: string;
  quantity: number;
  unitPrice: string;
  totalPrice: string;
  reservationStatus: 'RESERVED' | 'COMMITTED' | 'RELEASED';
}
