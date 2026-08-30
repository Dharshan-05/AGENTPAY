'use client';
export type ShippingRatesTabType = 'RATE_MATRIX' | 'CARRIERS' | 'ROUTING_RULES' | 'FUEL_SURCHARGES' | 'DELIVERY_ESTIMATES' | 'COMPARISON' | 'AUDIT';
export interface ShippingRateRecord {
  id: string;
  rateId: string;
  carrier: string;
  service: string;
  originRegion: string;
  destRegion: string;
  baseRate: string;
  deliveryEst: string;
  status: 'ACTIVE' | 'INACTIVE';
}
