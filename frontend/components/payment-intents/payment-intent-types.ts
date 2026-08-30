'use client';

export type PaymentIntentTabType = 'REGISTRY' | 'INTENTS' | 'AUTHORIZATION' | 'PROCESSING' | 'ROUTING' | 'RISK' | 'FAILURES' | 'AUDIT';

export interface PaymentIntentRecord {
  id: string;
  intentId: string;
  amount: string;
  currency: string;
  customer: string;
  agentId: string;
  paymentMethod: string;
  status: 'SUCCEEDED' | 'AUTHORIZED' | 'PROCESSING' | 'REQUIRES_ACTION' | 'FAILED' | 'CANCELED';
  processor: string;
  riskScore: number;
  authCode: string;
  createdAt: string;
}
