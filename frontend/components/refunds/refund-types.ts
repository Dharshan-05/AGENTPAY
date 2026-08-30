'use client';

export type RefundTabType = 'REGISTRY' | 'REQUESTS' | 'PROCESSING' | 'PARTIAL_REFUNDS' | 'FULL_REFUNDS' | 'FAILED' | 'AUDIT';

export interface RefundRecord {
  id: string;
  refundId: string;
  transactionId: string;
  paymentIntentId: string;
  amount: string;
  currency: string;
  reason: string;
  requestedBy: string;
  agentId: string;
  status: 'SUCCEEDED' | 'PROCESSING' | 'FAILED' | 'REQUESTED';
  processor: string;
  createdAt: string;
}
