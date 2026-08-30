import { TaxRateRecord } from './tax-rate-types';
export const MOCK_TAX_RATES: TaxRateRecord[] = [
  { id: 't1', taxRateId: 'TXR-AGP-001', jurisdiction: 'US — California', taxType: 'SALES_TAX', rate: '8.25%', nexusStatus: 'ACTIVE_NEXUS', status: 'ACTIVE' },
  { id: 't2', taxRateId: 'TXR-AGP-002', jurisdiction: 'EU — Germany', taxType: 'STANDARD_VAT', rate: '19.00%', nexusStatus: 'ACTIVE_NEXUS', status: 'ACTIVE' },
];
