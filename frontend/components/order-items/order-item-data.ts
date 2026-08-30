import { OrderItemRecord } from './order-item-types';
export const MOCK_ORDER_ITEMS: OrderItemRecord[] = [
  { id: 'oi1', orderItemId: 'ORI-AGP-001', orderId: 'ORD-AGP-001', productName: 'Autonomous Compute Credits (100k)', sku: 'SKU-COMPUTE-100K', quantity: 2, unitPrice: '$499.00', totalPrice: '$998.00', reservationStatus: 'COMMITTED' },
  { id: 'oi2', orderItemId: 'ORI-AGP-002', orderId: 'ORD-AGP-001', productName: 'Enterprise AgentGuard License', sku: 'SKU-GOV-ANNUAL', quantity: 1, unitPrice: '$12,001.00', totalPrice: '$12,001.00', reservationStatus: 'COMMITTED' },
];
