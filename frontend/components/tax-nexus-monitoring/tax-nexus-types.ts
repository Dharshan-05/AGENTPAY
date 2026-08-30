'use client';
export type TaxNexusMonitoringTabType = 'NEXUS_JURISDICTIONS' | 'ECONOMIC_THRESHOLDS' | 'TAX_LIABILITIES' | 'AUDIT';
export interface TaxNexusRecord {
  id: string;
  nexusId: string;
  jurisdiction: string;
  salesVolume: string;
  thresholdLimit: string;
  percentageReached: string;
  nexusStatus: 'NEXUS_REACHED' | 'APPROACHING_THRESHOLD';
}
