'use client';
export type TaxesTabType = 'JURISDICTIONS' | 'CALCULATIONS' | 'EXEMPTIONS' | 'VAT_GST' | 'RETURNS' | 'REPORTS' | 'AUDIT';
export interface TaxRecord {
  id: string;
  taxId: string;
  jurisdiction: string;
  taxType: 'US_SALES_TAX' | 'EU_VAT' | 'UK_VAT' | 'INDIA_GST';
  taxRate: string;
  taxCollected: string;
  status: 'REMITTED' | 'PENDING_REMITTANCE';
}
