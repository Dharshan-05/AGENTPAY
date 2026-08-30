import { TaxRecord } from './tax-types';
export const MOCK_TAXES: TaxRecord[] = [
  { id: 't1', taxId: 'TAX-AGP-001', jurisdiction: 'United States — California', taxType: 'US_SALES_TAX', taxRate: '8.25%', taxCollected: '$1,385.60', status: 'PENDING_REMITTANCE' },
  { id: 't2', taxId: 'TAX-AGP-002', jurisdiction: 'European Union — Germany', taxType: 'EU_VAT', taxRate: '19.00%', taxCollected: '€96,691.00', status: 'REMITTED' },
];
