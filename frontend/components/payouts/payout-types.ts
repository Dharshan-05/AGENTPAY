'use client';

export type PayoutTabType = 'REGISTRY' | 'SCHEDULED' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'BANK_ACCOUNTS' | 'RISK' | 'AUDIT';

export interface PayoutRecord {
  id: string;
  payoutId: string;
  merchantId: string;
  amount: string;
  currency: string;
  destination: string;
  bankName: string;
  processor: string;
  status: 'COMPLETED' | 'PROCESSING' | 'SCHEDULED' | 'FAILED';
  expectedArrival: string;
  riskScore: number;
}
