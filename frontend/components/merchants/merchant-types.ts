'use client';

export type MerchantTabType = 'REGISTRY' | 'PROFILES' | 'ACCOUNTS' | 'PAYMENT_METHODS' | 'PROCESSORS' | 'RISK' | 'SETTLEMENTS' | 'AUDIT';

export interface MerchantRecord {
  id: string;
  merchantId: string;
  businessName: string;
  country: string;
  industry: string;
  processor: string;
  settlementCurrency: string;
  volume: string;
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH';
  accountStatus: 'ACTIVE' | 'VERIFIED' | 'SUSPENDED';
  lastSettlement: string;
}
