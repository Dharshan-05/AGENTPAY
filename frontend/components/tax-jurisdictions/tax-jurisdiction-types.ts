'use client';
export type TaxJurisdictionsTabType = 'JURISDICTIONS' | 'NEXUS_THRESHOLDS' | 'EXEMPTION_CERTIFICATES' | 'CROSS_BORDER' | 'AUDIT';
export interface TaxJurisdictionRecord {
  id: string;
  jurisdictionId: string;
  regionName: string;
  taxType: 'SALES_TAX' | 'VAT' | 'GST';
  standardRate: string;
  economicNexusMet: boolean;
  filingCadence: string;
  status: 'ACTIVE' | 'INACTIVE';
}
