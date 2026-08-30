'use client';
export type ShipmentDispatchTabType = 'SHIPMENTS' | 'CARRIERS' | 'TRACKING_FEEDS' | 'DISPATCH_RULES' | 'EXCEPTIONS' | 'AUDIT';
export interface ShipmentDispatchRecord {
  id: string;
  dispatchId: string;
  orderRef: string;
  carrier: 'FEDEX_EXPRESS' | 'DHL_EXPRESS' | 'UPS_WORLDWIDE';
  trackingNumber: string;
  origin: string;
  destination: string;
  estimatedDelivery: string;
  status: 'IN_TRANSIT' | 'DELIVERED' | 'DISPATCHED';
}
