'use client';
export type StoreCreditTabType = 'BALANCES' | 'ADJUSTMENTS' | 'AUTO_APPLY' | 'EXPIRATIONS' | 'LEDGER' | 'RECONCILIATION' | 'AUDIT';
export interface StoreCreditRecord {
  id: string;
  creditId: string;
  customer: string;
  balance: string;
  currency: string;
  lastMovement: string;
  autoApply: boolean;
  status: 'ACTIVE' | 'FROZEN';
}
