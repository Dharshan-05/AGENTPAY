'use client';
export type OrderItemBreakdownTabType = 'ITEMS' | 'LINE_TAX' | 'DISCOUNT_SPLITS' | 'RESERVATIONS' | 'RETURNS_ELIGIBILITY' | 'AUDIT';
export interface OrderItemBreakdownRecord {
  id: string;
  itemId: string;
  orderRef: string;
  sku: string;
  quantity: number;
  unitPrice: string;
  taxAmount: string;
  lineTotal: string;
  returnEligible: boolean;
  status: 'ALLOCATED' | 'SHIPPED';
}
