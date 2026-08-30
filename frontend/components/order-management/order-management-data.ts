import { OrderManagementRecord } from './order-management-types';
export const MOCK_ORDER_MANAGEMENT: OrderManagementRecord[] = [
  { id: 'om1', orderId: 'OMGT-AGP-001', customerRef: 'CUS-AGP-001', merchantRef: 'MER-AGP-001', agentRef: 'AGT-892', totalValue: '$15,399.00', paymentState: 'PAID', fulfillmentState: 'FULFILLED', status: 'COMPLETED' },
  { id: 'om2', orderId: 'OMGT-AGP-002', customerRef: 'CUS-AGP-002', merchantRef: 'MER-AGP-002', agentRef: 'AGT-441', totalValue: '€3,200.00', paymentState: 'PAID', fulfillmentState: 'PROCESSING', status: 'ACTIVE' },
];
