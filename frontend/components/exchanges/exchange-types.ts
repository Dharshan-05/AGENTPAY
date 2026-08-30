'use client';
export type ExchangesTabType = 'EXCHANGES' | 'SKU_SWAPS' | 'PRICE_VARIANCE' | 'SHIPPING' | 'COMPLETED' | 'AUDIT';
export interface ExchangeRecord {
  id: string;
  exchangeId: string;
  orderId: string;
  originalSku: string;
  newSku: string;
  priceVariance: string;
  varianceStatus: 'EVEN_EXCHANGE' | 'CUSTOMER_OWES' | 'STORE_CREDIT_DUE';
  status: 'COMPLETED' | 'IN_PROCESSING';
}
