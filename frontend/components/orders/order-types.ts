'use client';
export type OrdersTabType = 'REGISTRY' | 'PAYMENT_PENDING' | 'PAID' | 'PROCESSING' | 'FULFILLED' | 'COMPLETED' | 'CANCELLED' | 'AUDIT';
export interface OrderRecord {
  id: string;
  orderId: string;
  customer: string;
  merchant: string;
  agentId: string;
  itemCount: number;
  totalAmount: string;
  paymentState: 'PAID' | 'PAYMENT_PENDING' | 'FAILED';
  fulfillmentState: 'FULFILLED' | 'PROCESSING' | 'UNFULFILLED';
  orderState: 'COMPLETED' | 'ACTIVE' | 'CANCELLED';
}
