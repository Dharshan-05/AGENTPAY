import { ExchangeRecord } from './exchange-types';
export const MOCK_EXCHANGES: ExchangeRecord[] = [
  { id: 'e1', exchangeId: 'EXC-AGP-001', orderId: 'ORD-AGP-001', originalSku: 'SKU-COMPUTE-100K', newSku: 'SKU-COMPUTE-250K', priceVariance: '+$499.00', varianceStatus: 'CUSTOMER_OWES', status: 'COMPLETED' },
  { id: 'e2', exchangeId: 'EXC-AGP-002', orderId: 'ORD-AGP-002', originalSku: 'SKU-GOV-ANNUAL', newSku: 'SKU-GOV-MONTHLY', priceVariance: '-€1,000.00', varianceStatus: 'STORE_CREDIT_DUE', status: 'IN_PROCESSING' },
];
