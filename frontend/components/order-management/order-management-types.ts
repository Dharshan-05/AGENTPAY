'use client';
export type OrderManagementTabType = 'ORDERS' | 'FULFILLMENT_MATRIX' | 'PAYMENT_STATES' | 'AGENT_ORIGINATED' | 'COMPLETED' | 'CANCELLED' | 'AUDIT';
export interface OrderManagementRecord {
  id: string;
  orderId: string;
  customerRef: string;
  merchantRef: string;
  agentRef: string;
  totalValue: string;
  paymentState: 'PAID' | 'PENDING' | 'FAILED';
  fulfillmentState: 'FULFILLED' | 'PROCESSING' | 'UNFULFILLED';
  status: 'COMPLETED' | 'ACTIVE' | 'CANCELLED';
}
