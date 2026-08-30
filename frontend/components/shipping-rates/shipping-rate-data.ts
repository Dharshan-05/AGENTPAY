import { ShippingRateRecord } from './shipping-rate-types';
export const MOCK_SHIPPING_RATES: ShippingRateRecord[] = [
  { id: 'sr1', rateId: 'RAT-AGP-001', carrier: 'FedEx Express', service: 'PRIORITY_OVERNIGHT', originRegion: 'US-East', destRegion: 'US-West', baseRate: '$45.00', deliveryEst: '1 Business Day', status: 'ACTIVE' },
  { id: 'sr2', rateId: 'RAT-AGP-002', carrier: 'DHL Express', service: 'EXPRESS_WORLDWIDE', originRegion: 'US-East', destRegion: 'EU-Central', baseRate: '€65.00', deliveryEst: '2 Business Days', status: 'ACTIVE' },
];
