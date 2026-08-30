'use client';
export type SupplierPayoutsTabType = 'PAYOUTS' | 'VENDORS' | 'SPLIT_RULES' | 'BATCHES' | 'SETTLED' | 'HELD' | 'AUDIT';
export interface SupplierPayoutRecord {
  id: string;
  payoutId: string;
  vendorName: string;
  amount: string;
  currency: string;
  splitPercentage: string;
  status: 'SETTLED' | 'HELD' | 'PROCESSING';
}
