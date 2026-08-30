import { ReturnRecord } from './return-types';
export const MOCK_RETURNS: ReturnRecord[] = [
  { id: 'r1', rmaId: 'RMA-AGP-001', orderId: 'ORD-AGP-001', customer: 'CUS-AGP-001 (Acme AI)', reason: 'DEFECTIVE_HARDWARE', refundAmount: '$499.00', inspectionState: 'PASSED', status: 'COMPLETED' },
  { id: 'r2', rmaId: 'RMA-AGP-002', orderId: 'ORD-AGP-002', customer: 'CUS-AGP-002 (Global Tech)', reason: 'INCOMPATIBLE_SPECS', refundAmount: '€1,200.00', inspectionState: 'PENDING', status: 'IN_INSPECTION' },
];
