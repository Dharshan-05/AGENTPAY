import { OrderRecord } from './order-types';
export const MOCK_ORDERS: OrderRecord[] = [
  { id: 'o1', orderId: 'ORD-AGP-001', customer: 'CUS-AGP-001', merchant: 'MER-AGP-001', agentId: 'AGT-892', itemCount: 2, totalAmount: '$12,999.00', paymentState: 'PAID', fulfillmentState: 'FULFILLED', orderState: 'COMPLETED' },
  { id: 'o2', orderId: 'ORD-AGP-002', customer: 'CUS-AGP-002', merchant: 'MER-AGP-002', agentId: 'AGT-441', itemCount: 1, totalAmount: '€2,499.00', paymentState: 'PAID', fulfillmentState: 'PROCESSING', orderState: 'ACTIVE' },
];
