'use client';
export type SubscriptionsTabType = 'REGISTRY' | 'PLANS' | 'TRIALS' | 'RENEWALS' | 'CANCELLATIONS' | 'DUNNING' | 'EVENTS' | 'AUDIT';
export interface SubscriptionRecord {
  id: string;
  subscriptionId: string;
  planName: string;
  customer: string;
  agentId: string;
  amount: string;
  interval: string;
  status: 'ACTIVE' | 'TRIALING' | 'PAST_DUE' | 'CANCELED';
  currentPeriodEnd: string;
  paymentMethod: string;
  riskScore: number;
}
