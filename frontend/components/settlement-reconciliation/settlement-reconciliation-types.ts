'use client';
export type SettlementReconciliationTabType = 'BATCHES' | 'MATCHED' | 'DISCREPANCIES' | 'BANK_FEEDS' | 'FEE_DEDUCTIONS' | 'AUDIT';
export interface SettlementReconciliationRecord {
  id: string;
  batchId: string;
  processor: string;
  grossAmount: string;
  feesDeducted: string;
  netSettled: string;
  matchedTransactions: number;
  variance: string;
  status: 'RECONCILED' | 'UNMATCHED';
}
