'use client';
export type DiscrepancyResolutionTabType = 'EXCEPTIONS' | 'AUTOMATED_ADJUSTMENTS' | 'WRITE_OFFS' | 'AUDIT';
export interface DiscrepancyResolutionRecord {
  id: string;
  discrepancyId: string;
  ledgerEntryRef: string;
  processorRef: string;
  varianceAmount: string;
  discrepancyReason: string;
  resolutionStrategy: string;
  status: 'RESOLVED' | 'UNDER_INVESTIGATION';
}
