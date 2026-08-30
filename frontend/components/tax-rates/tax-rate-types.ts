'use client';
export type TaxRatesTabType = 'RATES' | 'NEXUS_RULES' | 'JURISDICTIONS' | 'EXEMPTIONS' | 'FILING_SCHEDULE' | 'AUDIT';
export interface TaxRateRecord {
  id: string;
  taxRateId: string;
  jurisdiction: string;
  taxType: string;
  rate: string;
  nexusStatus: 'ACTIVE_NEXUS' | 'NON_NEXUS';
  status: 'ACTIVE' | 'ARCHIVED';
}
