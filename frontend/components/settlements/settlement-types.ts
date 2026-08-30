'use client';

export type SettlementTabType = 'REGISTRY' | 'BATCHES' | 'PROCESSORS' | 'MERCHANTS' | 'RECONCILIATION' | 'EXCEPTIONS' | 'TIMELINE' | 'AUDIT';

export interface SettlementRecord {
  id: string;
  settlementId: string;
  batchId: string;
  merchantId: string;
  processor: string;
  grossAmount: string;
  fees: string;
  netAmount: string;
  currency: string;
  settlementDate: string;
  status: 'SETTLED' | 'PROCESSING' | 'HOLD';
  ledgerRef: string;
}
