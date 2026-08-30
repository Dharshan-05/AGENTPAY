import { ShippingRecord } from './shipping-types';
export const MOCK_SHIPPING: ShippingRecord[] = [
  { id: 's1', shipmentId: 'SHP-AGP-001', orderId: 'ORD-AGP-001', carrier: 'FedEx Express', service: 'PRIORITY_OVERNIGHT', trackingId: '782910492100', destination: 'San Francisco, CA, US', shippingCost: '$45.00', status: 'DELIVERED' },
  { id: 's2', shipmentId: 'SHP-AGP-002', orderId: 'ORD-AGP-002', carrier: 'DHL Express', service: 'EXPRESS_WORLDWIDE', trackingId: '992104821019', destination: 'Berlin, DE', shippingCost: '€65.00', status: 'IN_TRANSIT' },
];
