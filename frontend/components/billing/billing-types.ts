'use client';
export type BillingTabType = 'CYCLES' | 'USAGE' | 'CHARGES' | 'CREDITS' | 'TAXES' | 'BALANCES' | 'PROFILES' | 'AUDIT';
export interface BillingRecord {
  id: string;
  billingId: string;
  customer: string;
  cyclePeriod: string;
  usageUnits: number;
  meteredAmount: string;
  balance: string;
  status: 'CURRENT' | 'OVERDUE' | 'CREDIT_POSITIVE';
}
