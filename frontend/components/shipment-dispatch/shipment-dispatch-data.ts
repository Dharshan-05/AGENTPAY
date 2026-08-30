import { ShipmentDispatchRecord } from './shipment-dispatch-types';
export const MOCK_SHIPMENT_DISPATCH: ShipmentDispatchRecord[] = [
  { id: 'sd1', dispatchId: 'SDSP-AGP-001', orderRef: 'OMGT-AGP-001', carrier: 'FEDEX_EXPRESS', trackingNumber: 'TRK-992184-US', origin: 'US-EAST-1 (VA)', destination: 'San Francisco, CA', estimatedDelivery: '2026-08-31 14:00', status: 'IN_TRANSIT' },
  { id: 'sd2', dispatchId: 'SDSP-AGP-002', orderRef: 'OMGT-AGP-002', carrier: 'DHL_EXPRESS', trackingNumber: 'TRK-441092-EU', origin: 'EU-WEST-1 (DE)', destination: 'London, UK', estimatedDelivery: '2026-09-01 10:30', status: 'DISPATCHED' },
];
