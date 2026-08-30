'use client';

export type CustomerTabType = 'REGISTRY' | 'PROFILES' | 'IDENTITY' | 'AGENTS' | 'PAYMENT_METHODS' | 'RISK' | 'ACTIVITY' | 'AUDIT';

export interface CustomerRecord {
  id: string;
  customerId: string;
  name: string;
  emailMasked: string;
  country: string;
  currency: string;
  verificationState: 'VERIFIED' | 'PENDING' | 'KYC_REQUIRED' | 'SUSPENDED';
  linkedAgentId: string;
  paymentMethod: string;
  riskScore: number;
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH';
  txnCount: number;
  totalVolume: string;
  status: 'ACTIVE' | 'FLAGGED' | 'INACTIVE';
  lastActivity: string;
}
