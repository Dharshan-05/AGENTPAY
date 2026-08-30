'use client';
export type FeesTabType = 'INTERCHANGE' | 'NETWORK_FEES' | 'PLATFORM_MARGIN' | 'SCHEME_FEES' | 'PROCESSOR_SPLIT' | 'RECONCILIATION' | 'AUDIT';
export interface FeeRecord {
  id: string;
  feeId: string;
  transactionRef: string;
  processor: string;
  interchangeFee: string;
  schemeFee: string;
  platformMargin: string;
  totalFees: string;
  effectiveRate: string;
}
