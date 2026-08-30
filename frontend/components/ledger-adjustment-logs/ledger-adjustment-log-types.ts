'use client';
export type LedgerAdjustmentLogsTabType = 'ADJUSTMENT_LOGS' | 'MANUAL_CORRECTIONS' | 'RECONCILIATION_OFFSETS' | 'AUDIT';
export interface LedgerAdjustmentRecord {
  id: string;
  adjustmentId: string;
  ledgerAccount: string;
  adjustmentType: 'CREDIT_OFFSET' | 'DEBIT_CORRECTION';
  amount: string;
  reasonCode: string;
  approverRef: string;
  status: 'POSTED_IMMUTABLE' | 'PENDING_APPROVAL';
}
