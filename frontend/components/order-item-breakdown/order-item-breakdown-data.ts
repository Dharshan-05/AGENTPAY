import { OrderItemBreakdownRecord } from './order-item-breakdown-types';
export const MOCK_ORDER_ITEM_BREAKDOWN: OrderItemBreakdownRecord[] = [
  { id: 'ob1', itemId: 'OIBR-AGP-001', orderRef: 'OMGT-AGP-001', sku: 'SKU-INF-10M-V1', quantity: 5, unitPrice: '$899.00', taxAmount: '$370.84', lineTotal: '$4,865.84', returnEligible: true, status: 'SHIPPED' },
  { id: 'ob2', itemId: 'OIBR-AGP-002', orderRef: 'OMGT-AGP-002', sku: 'SKU-SEC-ENT-ANNUAL', quantity: 1, unitPrice: '$14,500.00', taxAmount: '$1,196.25', lineTotal: '$15,696.25', returnEligible: false, status: 'ALLOCATED' },
];
