import { TaxJurisdictionRecord } from './tax-jurisdiction-types';
export const MOCK_TAX_JURISDICTIONS: TaxJurisdictionRecord[] = [
  { id: 'tj1', jurisdictionId: 'TJUR-AGP-001', regionName: 'United States — California (CA)', taxType: 'SALES_TAX', standardRate: '8.25%', economicNexusMet: true, filingCadence: 'MONTHLY', status: 'ACTIVE' },
  { id: 'tj2', jurisdictionId: 'TJUR-AGP-002', regionName: 'European Union — Germany (DE)', taxType: 'VAT', standardRate: '19.00%', economicNexusMet: true, filingCadence: 'QUARTERLY', status: 'ACTIVE' },
];
