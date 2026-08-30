'use client';
export type ShippingTabType = 'SHIPMENTS' | 'CARRIERS' | 'LABEL_GENERATION' | 'IN_TRANSIT' | 'DELIVERED' | 'EXCEPTIONS' | 'AUDIT';
export interface ShippingRecord {
  id: string;
  shipmentId: string;
  orderId: string;
  carrier: string;
  service: string;
  trackingId: string;
  destination: string;
  shippingCost: string;
  status: 'DELIVERED' | 'IN_TRANSIT' | 'LABEL_CREATED';
}
